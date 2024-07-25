{
  description = "Tool to show my university shedule in my waybar";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
  };

  outputs = { self, nixpkgs }:
    let
      # Helper function to generate an attrset '{ x86_64-linux = f "x86_64-linux"; ... }'.
      forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed;
    in
    {
      packages = forAllSystems (system:
        let pkgs = import nixpkgs { inherit system; };
        in
        rec {
          default = pkgs.python3Packages.buildPythonApplication rec {
            pname = "usw";
            # Performing black magic
            # Don't worry, I sacrificed enough goats for the next few years
            version = (pkgs.lib.importTOML ./USW/version.py).VERSION;
            format = "pyproject";

            src = ./.;

            nativeBuildInputs = with pkgs.python3Packages; [
              setuptools
            ];

            propagatedBuildInputs = with pkgs.python3Packages; [
		icalendar
		recurring-ical-events
		requests
            ];
          };
        });
    };
}
