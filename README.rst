A basic server client tool for image manipulation using GRPC.
This was written for an interview with Neuralink Corp.

Installation
-------------------------------------------------------------------------------------------------
To run the installation, 
1. run  ``sudo ./setup`` in the project's root directory.
   *sudo is optional, but recommended. Some permission issues could occur causing installs to fail*

   *To verify if the installation worked fine, you may run the unit tests.*

2. run ``pytest tests/`` from the root directory.

   *If all tests pass, the installation worked.*


*Whenever opening a new terminal to run the server or client, run `./start_terminal` from the root directory to set the correct python environment.*
-----------------------------------------------------------------------------------------------------------------------------------------

Running the Server
--------------------------------------------------------------------------------------------------

1. Start a new terminal

2. cd into the root directory of this package

3. run: ``./start_terminal``
   *This should make a new poetry shell*

4. Enter the command: ``server --host-name MY_HOST --port MY_PORT``

    **run server --help to know all the options**

Running the Client
--------------------------------------------------------------------------------------------------
1. Start a new terminal

2. cd into the root directory of this package

3. run: ``./start_terminal``
   *This should make a new poetry shell*

4. Enter the command: ``client --host-name MY_HOST --port MY_PORT --input MY_IMAGE_PATH --output --MY_IMAGE_OUTPUT_PATH``

Example After Installation
--------------------------
   Terminal 1:  
      command1: ```./start_terminal```

      command2: ```server```

   Terminal 2:  
      command1: ```./start_terminal```

      command2: ```client --mean --input ./tests/testing_data/image.png --output data/my_output.png``

    **run client --help to know all the command line options**



