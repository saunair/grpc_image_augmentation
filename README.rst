A basic server client tool for image manipulation using GRPC.
This was written for an interview with Neuralink Corp.

Installation
-------------------------------------------------------------------------------------------------
To run the installation, 
1. run  ```./setup ``` in the project's root directory.


*Whenever opening a new terminal to run the server or client, run ./setup from the root directory to set the correct python environment.*

Running the Server
--------------------------------------------------------------------------------------------------

1. Start a new terminal

2. cd into the root directory of this package

3. run: ``./setup``
   *This should make a new poetry shell*

4. Enter the command: ``server --host-name MY_HOST --port MY_PORT``

    **run server --help to know all the options**

Running the Client
--------------------------------------------------------------------------------------------------
1. Start a new terminal

2. cd into the root directory of this package

3. run: ``./setup``
   *This should make a new poetry shell*

4. Enter the command: ``client --host-name MY_HOST --port MY_PORT --input MY_IMAGE_PATH --output --MY_IMAGE_OUTPUT_PATH``

    **run client --help to know all the command line options**


