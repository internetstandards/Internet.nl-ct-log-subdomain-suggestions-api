{ pkgs, ... }:

with pkgs; buildGoModule rec {
  pname = "certstream-server-go";
  version = "1.9.0";

  src = fetchFromGitHub {
    owner = "d-Rickyy-b";
    repo = pname;
    rev = "v${version}";
    hash = "sha256-jA7zIffCSsn045ORS8OZiCnSBD6x/ZCZSoPEu6R0DWM=";
  };

  vendorHash = "sha256-LNTGlUYgIS9G6SE65XgNDzEIwiD5ezZ87eXyNRZ0AfE=";

  postPatch = ''
    rm -rf vendor
    substituteInPlace go.mod \
      --replace-fail "go 1.25.0" "go ${go.version}" \
      --replace-fail "github.com/google/trillian v1.7.3" "github.com/google/trillian v1.7.2" \
      --replace-fail "golang.org/x/crypto v0.49.0" "golang.org/x/crypto v0.48.0" \
      --replace-fail "	github.com/sourcegraph/conc v0.3.1-0.20240121214520-5f936abd7ae8 // indirect
" "" \
      --replace-fail "golang.org/x/net v0.52.0" "golang.org/x/net v0.49.0" \
      --replace-fail "golang.org/x/sys v0.42.0" "golang.org/x/sys v0.41.0" \
      --replace-fail "golang.org/x/text v0.35.0" "golang.org/x/text v0.34.0" \
      --replace-fail "google.golang.org/genproto/googleapis/rpc v0.0.0-20260401024825-9d38bb4040a9" "google.golang.org/genproto/googleapis/rpc v0.0.0-20251222181119-0a764e51fe1b" \
      --replace-fail "google.golang.org/grpc v1.80.0" "google.golang.org/grpc v1.79.1" \
      --replace-fail "	google.golang.org/protobuf v1.36.11 // indirect
" "	google.golang.org/protobuf v1.36.11 // indirect
	gopkg.in/check.v1 v1.0.0-20190902080502-41f04d3bba15 // indirect
"
  '';

  modBuildPhase = ''
    runHook preBuild

    go mod tidy
    go mod vendor "''${goModVendorFlags[@]}"

    mkdir -p vendor

    runHook postBuild
  '';

  subPackages = [ "cmd/certstream-server-go" ];

  meta = with lib; {
    description = "This project aims to be a drop-in replacement for the certstream server by Calidog.";
    homepage = "https://github.com/d-Rickyy-b/certstream-server-go";
    license = licenses.mit;
  };
}
