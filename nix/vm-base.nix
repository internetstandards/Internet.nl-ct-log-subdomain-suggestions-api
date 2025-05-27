{ ... }:
{ lib, ... }: {
  system.stateVersion = "24.11";

  # Keep the base VM configuration valid when evaluated as a normal NixOS
  # system during `nix flake check`. Real deployments can override these.
  fileSystems."/" = lib.mkDefault {
    device = "none";
    fsType = "tmpfs";
  };
  boot.loader.grub.devices = lib.mkDefault [ "nodev" ];

  # Configure networking
  networking.useDHCP = false;
  networking.interfaces.eth0.useDHCP = true;

  # Create user "test"
  services.getty.autologinUser = "test";
  users.users.test.isNormalUser = true;

  # Enable passwordless ‘sudo’ for the "test" user
  users.users.test.extraGroups = [ "wheel" ];
  security.sudo.wheelNeedsPassword = false;

  # make boot a little less verbose
  boot.kernelParams = [ "quiet" ];
  boot.consoleLogLevel = 0;
}
