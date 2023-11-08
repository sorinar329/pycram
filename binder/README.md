# Pycram on BinderHub

Files for running Pycram on BinderHub.

## Quick Start

### Option 1: Test Image Locally (Under repo directory)

- Run Docker image

  ```bash
  docker compose -f ./binder/docker-compose.yml up
  ```

- Run Docker image with X-forwarding

  ```bash
  xhost +local:docker && \
  docker compose -f ./binder/docker-compose.yml up && \
  xhost -local:docker
  ```

- Open Web browser and go to http://localhost:8888/

- To stop and remove container:

  ```bash
  docker compose -f ./binder/docker-compose.yml down
  ```

- Force image rebuild

  ```bash
  docker compose -f ./binder/docker-compose.yml up -d --build
  ```

### Option 2: Run on BinderHub

- intro.ipynb: [![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/pycram.git/binder-xpra?urlpath=lab%2Ftree%2Fexamples%2Fintro.ipynb)

- Passing ROS paramters (robot=pr2, environment=kitchen): [![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/pycram.git/binder-xpra?urlpath=lab%2Ftree%2Fexamples%2Faction_designator.ipynb%3Frobot%3Dpr2%26environment%3Dkitchen)

## Usage

1. Open notebooks in [../examples](../examples)

1. PyCram Docs: https://pycram.readthedocs.io/en/latest/examples.html

## Files Descriptions

1. ***[Dockerfile](./Dockerfile):*** Pycram jupyterlab docker image.
1. ***[pycram-http.rosinstall](./pycram-http.rosinstall):*** Initiating ros workspace in docker image require https url. (Comparing to [pycram.rosinstall](../pycram.rosinstall): pycram is excluded, repo `orocos_kinematics_dynamics` is PyKDL).
1. ***[entrypoint.sh](./entrypoint.sh):*** Entrypoint of the docker image, start roscore and robot web tools.
1. ***[docker-compose.yml](./docker-compose.yml):*** For testing the docker image locally.