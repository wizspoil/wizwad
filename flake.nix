{
  description = "A fast extractor and packer for wizard101/pirate101 wad files";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts/";
    nix-systems.url = "github:nix-systems/default";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs @ {
    self,
    flake-parts,
    nix-systems,
    poetry2nix,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      debug = true;
      systems = import nix-systems;
      perSystem = {
        pkgs,
        self',
        ...
      }: let
        python = pkgs.python311;

        poetry2nix' = poetry2nix.lib.mkPoetry2Nix {inherit pkgs;};
      in {
        packages.wizwad = poetry2nix'.mkPoetryApplication {
          projectDir = ./.;
          inherit python;
        };

        packages.default = self'.packages.wizwad;

        devShells.default = pkgs.mkShell {
          name = "wizwad";
          packages = with pkgs; [
            (poetry.withPlugins (ps: with ps; [poetry-plugin-up]))
            python
            just
            alejandra
            python.pkgs.black
            python.pkgs.isort
          ];
        };
      };
    };
}
