{ pkgs, ...}:  pkgs.python3Packages.buildPythonPackage rec {
  pname = "simdjson";
  version = "7.0.1";
  pyproject = true;
  dontCheckRuntimeDeps = true;

  src = pkgs.python3Packages.fetchPypi {
    inherit version;
    pname = "pysimdjson";
    hash = "sha256-2moj2Mu5CW1B/m2ykGq25sCi9CplLJeB6vBSBJ/oeD8=";
  };
  build-system = with pkgs.python3Packages; [ setuptools cython ];
}
