{ pkgs, ... }: pkgs.python3Packages.buildPythonPackage rec {
  pname = "certstream";
  version = "1.12";
  pyproject = true;

  src = pkgs.python3Packages.fetchPypi {
    inherit pname version;
    hash = "sha256-5pLWXqlEel22zRRsWWmvZDTt2HFj/gsQCWK7XX0iPds=";
  };

  dependencies = with pkgs.python3Packages; [ websocket-client termcolor ];
  build-system = with pkgs.python3Packages; [ setuptools ];
}
