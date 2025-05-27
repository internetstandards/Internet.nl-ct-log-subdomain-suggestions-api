{ self }:
{ lib, config, pkgs, ... }:

let
  # shorthand for this module's configuration
  cfg = config.services.ctlssa;
  # current system for which package/module is built
  inherit (pkgs.stdenv.hostPlatform) system;
in {
  # define configurable options for this module
  options.services.ctlssa = {
    enable = lib.mkEnableOption "CTLSSA";
    port = lib.mkOption {
      type = lib.types.int;
      default = 8001;
      description = "The port on which the CTLSSA service will listen.";
    };
    allowedHosts = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "localhost" ];
      description = "The list of allowed hosts for the CTLSSA service.";
    };
    database.name = lib.mkOption {
      type = lib.types.str;
      default = "ctlssa";
      description = "Database name.";
    };
    user = lib.mkOption {
      type = lib.types.str;
      default = "ctlssa";
      description = "Name of the CTLSSA user.";
    };
    group = lib.mkOption {
      type = lib.types.str;
      default = "ctlssa";
      description = "Name of the CTLSSA group.";
    };
  };

  # implement the module configuration
  config = lib.mkIf cfg.enable {
    # configure user/group using for postgresql authentication amount others
    users.users."${cfg.user}" = {
      isSystemUser = true;
      group = cfg.group;
      home = "/var/lib/ctlssa";
      createHome = true;
    };
    users.groups."${cfg.group}" = { };

    # add the package to the system path for running management commands
    environment.systemPackages = let
      # using wrapper path instead of Nix store path as store might not always allow setuid (eg: inside VM)
      sudo = "/run/wrappers/bin/sudo";
    in [
      # wrap the actual application to configure Django and database settings
      (pkgs.writeShellScriptBin "ctlssa" ''
        export DJANGO_SETTINGS_MODULE=ctlssa.app.settings
        export CTLSSA_DJANGO_DATABASE=production
        export CTLSSA_DB_ENGINE=postgresql_psycopg2
        export CTLSSA_DB_HOST=/var/run/postgresql
        export CTLSSA_DB_NAME=${cfg.database.name}
        # execute command as configured user so DB can be accessed
        exec ${sudo} --preserve-env --user=${cfg.user} ${self.packages."${system}".ctlssa}/bin/ctlssa $@
      '')
    ];

    # configure a uWSGI instance to run ctlssa
    services.uwsgi = {
      enable = true;
      # enable python
      plugins = [ "python3" ];
      # needed to drop privileges
      capabilities = [ "CAP_SETUID" "CAP_SETGID" ];
      # configure the ctlssa uWSGI instance
      instance = {
        type = "normal";
        master = true;
        http-socket = ":${toString cfg.port}";
        immediate-uid = cfg.user;
        immediate-gid = cfg.user;
        module = "ctlssa.app.wsgi";
        # add the ctlssa package and all its dependencies to the PYTHONPATH for this uwsgi instance
        pythonPackages = (x: [ self.packages."${system}".ctlssa ]);
        # configuration Django
        env = [
          "DJANGO_SETTINGS_MODULE=ctlssa.app.settings"
          "DEBUG=False"
          "CTLSSA_DJANGO_DATABASE=production"
          "CTLSSA_DB_ENGINE=postgresql_psycopg2"
          "CTLSSA_DB_HOST=/var/run/postgresql"
          "CTLSSA_DB_NAME=${cfg.database.name}"
          "CTLSSA_HOSTNAMES=${builtins.concatStringsSep "," cfg.allowedHosts}"
        ];
      };
    };

    systemd.services.ctlssa-ingest = {
      enable = true;
      description = "Internet.nl Certificate Transparency Log Subdomain Suggestions Ingest";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      environment = {
        DJANGO_SETTINGS_MODULE = "ctlssa.app.settings";
        DEBUG = "False";
        CTLSSA_DJANGO_DATABASE = "production";
        CTLSSA_DB_ENGINE = "postgresql_psycopg2";
        # use postgresql socket path for connecting so we cn leverage unix user authentication
        CTLSSA_DB_HOST = "/var/run/postgresql";
        TLDEXTRACT_CACHE = "/var/cache/tldextract";
        CTLSSA_CERTSTREAM_SERVER_URL = "ws://127.0.0.1:4000";
        # PYTHONPATH = "${self.packages."${system}".ctlssa.pythonPath}";
      };
      serviceConfig = {
        User = cfg.user;
        ExecStartPre = "${self.packages.${system}.ctlssa}/bin/ctlssa migrate";
        ExecStart = "${self.packages.${system}.ctlssa}/bin/ctlssa ingest";
        CacheDirectory = "tldextract";
      };
    };

    services.postgresql = {
      enable = true;
      ensureDatabases = [ cfg.database.name ];
      ensureUsers = [{
        name = cfg.user;
        ensureDBOwnership = true;
      }];
    };

    systemd.services.certstream-server = let
      config = pkgs.writeText "config.yaml" ''
        webserver:
          listen_addr: "127.0.0.1"
          listen_port: 4000
          full_url: "/full-stream"
          lite_url: "/"
          domains_only_url: "/domains-only"
          cert_path: ""
          cert_key_path: ""
          compression_enabled: false

        prometheus:
          enabled: true
          listen_addr: "127.0.0.1"
          listen_port: 4000
          metrics_url: "/metrics"
          expose_system_metrics: false
          real_ip: false
          whitelist:
            - "127.0.0.1/8"

        general:
          # When you want to add logs that are not contained in the log list provided by
          # Google (https://www.gstatic.com/ct/log_list/v3/log_list.json), you can add them here.
          # additional_logs:
          #   - url: https://ct.googleapis.com/logs/us1/mirrors/digicert_nessie2022
          #     operator: "DigiCert"
          #     description: "DigiCert Nessie2022 log"
          #   - url: https://dodo.ct.comodo.com
          #     operator: "Comodo"
          #     description: "Comodo Dodo"
          # To optimize the performance of the server, you can overwrite the size of different buffers
          # For low CPU, low memory machines, you should reduce the buffer sizes to save memory in case the CPU is maxed.
          buffer_sizes:
            # Buffer for each websocket connection
            websocket: 300
            # Buffer for each CT log connection
            ctlog: 1000
            # Combined buffer for the broadcast manager
            broadcastmanager: 10000
          # Google regularly updates the log list. If this option is set to true, the server will remove all logs no longer listed in the Google log list.
          # This option defaults to true. See https://github.com/d-Rickyy-b/certstream-server-go/issues/51
          drop_old_logs: true
      '';
    in {
      enable = true;
      description =
        "A service to aggregate, parse, and stream certificate data from multiple certificate transparency logs.";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];

      serviceConfig = {
        User = cfg.user;
        Group = cfg.group;
        ExecStart = "${self.packages.${system}.certstream-server-go}/bin/certstream-server-go --config ${config}";
      };
    };
  };
}
