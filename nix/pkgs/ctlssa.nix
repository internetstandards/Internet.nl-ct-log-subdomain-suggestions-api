{ self, pkgs, ... }: pkgs.python3Packages.buildPythonPackage rec {
  pname = "ctlssa";
  version = "0.0.1";
  pyproject = true;

  src = self;

  # dependencies for building/running this package
  dependencies = (with pkgs.python3Packages;
    [ colorlog tldextract django python-xz psycopg ]) ++ [
    pkgs.uwsgi
    # add Python dependencies that are not available in the NixOS package repository
    (pkgs.callPackage ./certstream.nix { inherit pkgs; })
    (pkgs.callPackage ./pysimdjson.nix { inherit pkgs; })
  ];

  # required to add dependencies to Python environment for CTLSSA
  propagatedBuildInputs = dependencies;

  # required for pyproject
  build-system = with pkgs.python3Packages; [ setuptools setuptools-scm ];
}
