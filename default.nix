{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.gcc
    pkgs.zlib
    pkgs.openssl
    pkgs.libffi
    pkgs.pkg-config
  ];
}
