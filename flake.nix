{
  description = "A fast extractor and packer for wizard101/pirate101 wad files";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts/";
    nix-systems.url = "github:nix-systems/default";
  };

  outputs = inputs @ {
    self,
    flake-parts,
    nix-systems,
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
      in {
        devShells.default = pkgs.mkShell {
          name = "wizwad";
          packages = with pkgs; [
            uv
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
