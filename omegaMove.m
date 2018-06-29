% Make sure to have the server side running in V-REP: 
% in a child script of a V-REP scene, add following command
% to be executed just once, at simulation start:
%
% simRemoteApi.start(19999)
%
% then start simulation, and run this program.
%
% IMPORTANT: for each successful call to simxStart, there
% should be a corresponding call to simxFinish at the end!

function omegaMove()
    disp('Program started');
    % vrep=remApi('remoteApi','extApi.h'); % using the header (requires a compiler)
    vrep=remApi('remoteApi'); % using the prototype file (remoteApiProto.m)
    vrep.simxFinish(-1); % just in case, close all opened connections
    clientID=vrep.simxStart('127.0.0.1',19999,true,true,5000,5);
    
    if (clientID>-1)
        disp('Connected to remote API server');
            
        % Now try to retrieve data in a blocking fashion (i.e. a service call):
        %{
        [res,omega_left]=vrep.simxGetObjectHandle(clientID, 'Omega_leftMotor', vrep.simx_opmode_blocking);
        if (res==vrep.simx_return_ok)
            fprintf('Get Omega left handle\n');
        else
            fprintf('Remote API function call returned with error code: %d\n',res);
        end
        [res,omega_right]=vrep.simxGetObjectHandle(clientID, 'Omega_rightMotor', vrep.simx_opmode_blocking);
        if (res==vrep.simx_return_ok)
            fprintf('Get Omega right handle\n');
        else
            fprintf('Remote API function call returned with error code: %d\n',res);
        end
        %}
        
        % get collision handle
        [res,collision]=vrep.simxGetCollisionHandle(clientID, 'Collision', vrep.simx_opmode_blocking);
        if (res==vrep.simx_return_ok)
            fprintf('Get Collision handle\n');
        else
            fprintf('Remote API function call returned with error code: %d\n',res);
        end
        
        % get omega handle
        [res,omega]=vrep.simxGetObjectHandle(clientID, 'Omega', vrep.simx_opmode_blocking);
        if (res==vrep.simx_return_ok)
            fprintf('Get Omega handle\n');
        else
            fprintf('Remote API function call returned with error code: %d\n',res);
        end
            
        pause(2);
        
        % Move Omega following a straignt line until hit something
        p = [0,0.01,0];
        [res, retInts, retFloats, retStrings retBuffer] = vrep.simxCallScriptFunction(clientID, 'Omega', vrep.sim_scripttype_childscript, 'getContactObjects',[],[],[],[], vrep.simx_opmode_oneshot_wait);
        if (res==vrep.simx_return_ok)
                fprintf('Get collision status\n');
        else
           fprintf('Remote API function call returned with error code: %d\n',res);
        end
        while retFloats == 0
            res = vrep.simxSetObjectPosition(clientID, omega, omega, p, vrep.simx_opmode_oneshot_wait);
            if (res==vrep.simx_return_ok)
                fprintf('Omega Moving\n');
            else
                fprintf('Remote API function call returned with error code: %d\n',res);
            end
            [res, retInts, retFloats retStrings retBuffer] = vrep.simxCallScriptFunction(clientID, 'Omega', vrep.sim_scripttype_childscript, 'getContactObjects',[],[],[],[], vrep.simx_opmode_oneshot_wait);
            if (res==vrep.simx_return_ok)
                    fprintf('Get collision status\n');
            else
               fprintf('Remote API function call returned with error code: %d\n',res);
            end
        end
        
        retInts
        
        % set Omega position
        
        %{
        % Now retrieve streaming data (i.e. in a non-blocking fashion):
        t=clock;
        startTime=t(6);
        currentTime=t(6);
        vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming); % Initialize streaming
        while (currentTime-startTime < 5)   
            [returnCode,data]=vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_buffer); % Try to retrieve the streamed data
            if (returnCode==vrep.simx_return_ok) % After initialization of streaming, it will take a few ms before the first value arrives, so check the return code
                fprintf('Mouse position x: %d\n',data); % Mouse position x is actualized when the cursor is over V-REP's window
            end
            t=clock;
            currentTime=t(6);
        end
        %}
        % Now send some data to V-REP in a non-blocking fashion:
        vrep.simxAddStatusbarMessage(clientID,'Hello V-REP!',vrep.simx_opmode_oneshot);

        % Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
        vrep.simxGetPingTime(clientID);

        % Now close the connection to V-REP:    
        vrep.simxFinish(clientID);
    else
        disp('Failed connecting to remote API server');
    end
    vrep.delete(); % call the destructor!
    
    disp('Program ended');
end
