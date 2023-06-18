# show this list
default:
  just --list

# run tests
test:
  pytest --cov=wizwad

# format python and nix
format:
    isort . --skip-gitignore
    black .
    alejandra .
