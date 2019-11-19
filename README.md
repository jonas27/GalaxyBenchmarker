# Galaxy Benchmarker
A tool for benchmarking Galaxy job-destinations.

The goal is to easily benchmark different job-destinations. All you have to do is to configure the benchmarker itself,
define the destinations you want to benchmark, the workflows you want to run and the benchmarks you want to use. GalaxyBenchmarker
should handle the rest, like configuring Galaxy (to send the jobs to the right destination), submitting workflows and
collecting the metrics.

GalaxyBenchmarker is designed to be easily extendable in terms of destinations-types and benchmark-scenarios.

### Benchmark-Scenarios
Currently there are three types/scenarios of benchmarks available. Every benchmark allows to define its destination and workflows to test, how often workflows should
be run per destination and if some ansible-playbooks should be run before or after the benchmark ran.
#### Cold vs Warm
What is the difference between running a workflow for the first time or for it having been run multiple
times already? What is the overhead for staging time, installing tools, etc?

This benchmark cleans up Pulsar for every cold run, using a Ansible-Playbook ([coldwarm_pretask.yml]).

#### Destination Comparison
What are the differences between multiple destinations in terms of staging time (sending data
to a remote location might take some time), runtime, etc.

#### Burst
How does a destination handle a big burst of requests?


## Requirements
* A Galaxy-Instance with admin rights
* InfluxDB for saving the benchmark results
* Some job-destinations to benchmark
* Python 3.7
* Ansible

## Usage
### Install all dependencies
Some additional packages are needed in order for GalaxyBenchmarker to function properly. 
To install those, run the following command:
```shell
pip3 install -r requirements.txt
```

### Configure the GalaxyBenchmarker
To use the benchmarker, you first need to create a yaml-configuration file.
We need to have access to a Galaxy instance in order to submit workflows:
```yaml
galaxy:
  url: https://usegalaxy.eu
  user_key: YOUR-KEY
```

Next, we need to define the workflows that should be run. The benchmarker
uses the test functionality of [Planemo](https://github.com/galaxyproject/planemo) to 
submit workflows. Examples can be found at: https://github.com/usegalaxy-eu/workflow-testing. For a start, you
can clone this repository and use those workflows for benchmarking. Workflows are defined in the
configuration as following:
```yaml
workflows:
  - name: ARDWorkflow
    type: Galaxy
    path: /../workflow-testing/sklearn/ard/ard.ga
```

The benchmarker can submit jobs to multiple job destinations to compare the performance of each. For routing
the jobs to the right destination, users can be defined for each. The GalaxyBenchmarker can take 
care of that 
(see the [configuration examples](https://github.com/AndreasSko/Galaxy-Benchmarker/blob/master/benchmark_config.yml.example)) 
if you are an administrator for the Galaxy instance. Otherwise, it is also possible to use different
users for each destination and link them in the configuration of the benchmarker:
```yaml
destinations:
  - name: Destination1
    type: Galaxy
    galaxy_user_name: USERNAME
    galaxy_user_key: USERKEY
```

Now, we just need to define the actual benchmark that we want to perform. To compare different job destinations, 
you can do the following:
```yaml
benchmarks:
  - name: DestinationComparisonBenchmark
    type: DestinationComparison
    destinations:
      - Destination1
    workflows:
      - ARDWorkflow
    runs_per_workflow: 1
```

### Run the benchmarks
The GalaxyBenchmarker can use different configuration files. If none is given, it will look for `benchmark_config.yml`
```shell
python3 galaxy_benchmarker --config benchmark_config.yml
```

## Benchmark Types
### Destination Comparison
Used to compare the performance of different destinations.

#### Requirements
* 1-n Galaxy destinations
* 1-n Galaxy workflows
* `runs_per_workflow` >= 1: How many times should a workflow be run on every destination?

#### Optional settings
* `warmup`: if set to true, a "warmup run" will be performed for every workflow
on every destination, while its results won't be counted
* ``pre_task``/`post_task`: a task that will be run before or after the benchmark has been completed

### Cold vs Warm
Used to compare the performance of a cold run (workflows hasn't been run before) to a warm run. To 
simulate a cold run, you can define pre tasks that will be run before every cold workflow run, to
clean up caches etc.

Note: This benchmark type can only use one destination!

#### Requirements
* 1 Galaxy destination
* 1-n Galaxy workflows
* `runs_per_workflow` >= 1: How many times should a workflow be run on every destination?
* `cold_pre_task`: a task task that will be run in the cold phase before every workflow run

#### Optional settings
* ``pre_task``/`post_task`: a task that will be run before or after the benchmark has been completed
* `warm_pre_task`: a task task that will be run in the warm phase before every workflow run

### Burst
Used to start a burst of workflows at the same time. 

#### Requirements
* 1-n Galaxy destinations
* 1-n Galaxy workflows
* `runs_per_workflow` >= 1: How many times should a workflow be run on every destination?
* `burst_rate` > 0: How many workflows should be submitted per second? 
(for example: 0.5 results in a workflow submit every two seconds)

#### Optional settings
* `warmup`: if set to true, a "warmup run" will be performed for every workflow
on every destination, while its results won't be counted
* ``pre_task``/`post_task`: a task that will be run before or after the benchmark has been completed

## Destination Types
### Galaxy Destination
TODO

### Condor Destination
TODO

## Task Types
### Ansible Playbook
An Ansible Playbook can be run on every destination defined in a benchmark. 
Note: You will need to add `host`, `host_user` and `ssh_key` to the definition of 
every destination.
 
Define a task as follows:
```yaml
type: ansible-playbook
playbook: /path/to/playbook.yml
```

### Benchmarker Task
These are tasks defined in ``task.py``. Currently, there exist the following tasks:
* `delete_old_histories`: This will delete all histories of a user on Galaxy
* ``reboot_openstack_servers``: This will reboot all OpenStack instance which name correspond to
``name_contains``
* ``reboot_random_openstack_server``: This will reboot a randomly chosen OpenStack instance 
which name correspond to ``name_contains``
* ``rebuild_random_openstack_server``: This will rebuild a randomly chosen OpenStack instance 
which name correspond to ``name_contains``

Define a task as follows:
````yaml
type: benchmarker-task
name: task-name
params:
  param1: ab
  param2: cd
````

## Additional options
All possible options can be found in the [configuration examples](https://github.com/AndreasSko/Galaxy-Benchmarker/blob/master/benchmark_config.yml.example).

### InfluxDB
In normal cases, GalaxyBenchmarker will save the results in a json file under the `results` directory. However, job
metrics can also be submitted to InfluxDB for further analysis.
```yaml
influxdb:
  host: influxdb.example.com
  port: 8086
  username: glx_benchmarker_user
  password: supersecret
  db_name: glx_benchmarker
```
Example Dashboards for Grafana can be found at [grafana_dashboards](https://github.com/AndreasSko/Galaxy-Benchmarker/tree/master/grafana_dashboards)

### OpenStack
There exist some tasks that need access to OpenStack to work properly. For this,
you can define your credentials:
```yaml
openstack:
  auth_url: https://auth.url.com:5000/v3/
  compute_endpoint_version: 2.1
  username: username
  password: password
  project_id: id
  region_name: region
  user_domain_name: Default
```

### Let GalaxyBenchmarker handle the configuration 
The GalaxyBenchmarker can configure Galaxy to use different job destinations and to install 
tool dependencies. For that, you need have an admin user and SSH access to the instance.
```yaml
galaxy:
  ...
  # Install tool dependencies
  shed_install: true 
  # Should Galaxy be configured to use the given Destinations or is everything already set?
  configure_job_destinations: true
  ssh_user: ubuntu
  ssh_key: /local/path/to/ssh/key.cert
  galaxy_root_path: /srv/galaxy
  galaxy_config_dir: /srv/galaxy/server/config
  galaxy_user: galaxy
```
The settings for a new destination can then be defined as follows:
```yaml
destinations:
  - name: PulsarDestination
    type: PulsarMQ
    amqp_url: "pyamqp://username:password@rabbitmq.example.com:5672//"
    # If used for ColdWarmBenchmark, we need to have ssh-access to the Pulsar-Server
    host: pulsar.example.com
    host_user: centos
    ssh_key: /local/path/to/ssh/key.cert
    tool_dependency_dir: /data/share/tools
    jobs_directory_dir: /data/share/staging
    persistence_dir: /data/share/persisted_data
    # To configure additional params in job_conf.xml
    job_plugin_params:
      manager: __default__
    job_destination_params:
      dependency_resolution: remote
      default_file_action: remote_transfer
      remote_metadata: false
      rewrite_parameters: true
      amqp_acknowledge: true
      amqp_ack_republish_time: 10
```