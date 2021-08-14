A basic server client tool for image manipulation using GRPC.
This was written for an interview with Neuralink Corp.

To run the installation, run 
./setup 

Whenever opening a new terminal to run the server or client, run ./setup from the root directory to set the correct python environment.

To run the sever, 
1. open a new terminal
2. cd into the root directory of this package
3. run: ./setup
4. type: server --host-name MY_HOST --port MY_PORT 

    **run server --help to know all the options**

To run the sever, 
1. open a new terminal
2. cd into the root directory of this package
3. run: ./setup
4. type: client --host-name MY_HOST --port MY_PORT --input MY_IMAGE_PATH --output --MY_IMAGE_OUTPUT_PATH
    
  **run client --help to know all the command line options**


