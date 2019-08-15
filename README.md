# Item Catalog FSND Project 4


## Table of Contents

- [Intro](#intro)
- [Installation](#installation)
- [Instructions](#instructions)
- [Supporting Materials](#supporting-materials)

## Intro

This project was made to learn how to create a CRUD web app using Python. It uses a Google OAUTH2 to create content in this project.
It was develop using the Flask framework and SQL Alchemy to connect to the SQLite database. In the Frontend it uses Bootstrap and JQuery
for styling.

We're using tools called [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) to install and manage the VM. You'll need to install these to run this project.

## Installation

### Install VirtualBox

VirtualBox is the software that actually runs the virtual machine. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) Install the _platform package_ for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

**Ubuntu users:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center instead. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.

### Install Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [Download it from vagrantup.com.](https://www.vagrantup.com/downloads.html) Install the version for your operating system.

**Windows users:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

_If Vagrant is successfully installed, you will be able to run_ `vagrant --version`
_in your terminal to see the version number._
_The shell prompt in your terminal may differ. Here, the_ `$` _sign is the shell prompt._


## Instructions

### Start the virtual machine

From your terminal, inside the **vagrant** subdirectory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.

When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM.


### Running the project


1. Launch the Vagrant VM using command:

  ```
    $ vagrant up
  ```

2. Connect to the virtual machine using command:

  ```
    $ vagrant ssh
  ```

3. Run the database initiator:

  ```
    $ python /vagrant/catalog/init_db.py
  ```

4. Run the application within the VM:

  ```
    $ python /vagrant/catalog/views.py
  ```

5. Access and test your application by visiting [http://localhost:5000](http://localhost:5000).


## Supporting Materials

More info of the Virtual Machine on the Udacity repository:
[Virtual machine repository on GitHub](https://github.com/udacity/fullstack-nanodegree-vm)

[(Back to TOC)](#table-of-contents)
