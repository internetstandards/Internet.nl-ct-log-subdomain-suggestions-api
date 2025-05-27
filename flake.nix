{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };
  outputs = { self, nixpkgs, ... }:
    let
      # helper function to generate packages/devshells for every arch/OS combination we support
      forAllSystems = function:
        nixpkgs.lib.genAttrs [
          "aarch64-linux"
          "x86_64-linux"
          "aarch64-darwin"
          "x86_64-darwin"
        ]
        (system: function nixpkgs.legacyPackages.${system});
    in {
      packages = forAllSystems (pkgs: rec {
        # add ctlssa as the default package to be built for this flake
        default = ctlssa;
        # add package build for ctlssa
        ctlssa = pkgs.callPackage ./nix/pkgs/ctlssa.nix { inherit self pkgs; };
        certstream-server-go = pkgs.callPackage ./nix/pkgs/certstream-server-go.nix { inherit self pkgs; };
        # command for running CTLSSA on a VM on macOS (see below)
        darwinVM = self.nixosConfigurations.darwinVM.config.system.build.vm;
      });

      # export a module to be used in NixOS configurations
      nixosModules = {
        # the CTLSSA module itself to be used in other systems
        ctlssa = nixpkgs.lib.modules.importApply ./nix/module.nix { inherit self; };
        # base VM module for running CTLSSA in a local VM, eg: testing
        base = nixpkgs.lib.modules.importApply ./nix/vm-base.nix { inherit self; };
      };

      # create a shell configuration for running/developing CTLSSA using `nix develop` or Direnv
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          # set environment variables for running ctlssa in the development shell
          DJANGO_SETTINGS_MODULE = "ctlssa.app.settings";
          UWSGI_MODULE = "ctlssa.app.wsgi";
          UWSGI_HTTP_SOCKET = ":8001";
          UWSGI_MASTER = "1";
          UWSGI_UID = "nobody";
          DJANGO_PORT = "8001";
          # add ctlssa binary to the development shell
          buildInputs = [ self.packages."${pkgs.system}".ctlssa pkgs.nixos-rebuild ];
        };
      });

      # create a NixOS configuration for testing CTLSSA on a VM in Linux using `nixos-rebuild --flake .#linuxVM build-vm; ./result/bin/run-nixos-vm`
      nixosConfigurations.linuxVM = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [ self.nixosModules.ctlssa self.nixosModules.base ];
      };

      # create a NixOS configuration for testing CTLSSA on a VM in macOS using `nix run .#darwinVM`
      # https://www.tweag.io/blog/2023-02-09-nixos-vm-on-macos/
      nixosConfigurations.darwinVM = nixpkgs.lib.nixosSystem {
        system = "aarch64-linux";
        modules = [
          # include CTLSSA module
          self.nixosModules.ctlssa
          # enable CTLSSA
          {
            services.ctlssa.enable = true;
          }
          # include basic Linux system with networking and user settings
          self.nixosModules.base
          #
          {
            virtualisation.vmVariant.virtualisation = {
              # Make VM output to the terminal instead of a separate window
              graphics = false;
              # allow VM to run on macOS
              host.pkgs = nixpkgs.legacyPackages.aarch64-darwin;
            };
          }
        ];
      };
    };
}
