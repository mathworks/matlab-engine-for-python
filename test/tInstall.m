classdef tInstall < matlab.unittest.TestCase
% Verify installation of matlab engine

% Copyright 2023 Mathworks, Inc.

    properties (Constant)
        MATLABVersion = string(ver('MATLAB').Version) % Example: 9.14
    end

    methods (Test)
        function installMatchingEngine(testCase)
            [status, out] = system("pip install matlabengine==" + testCase.MATLABVersion + ".*");
            verifyEqual(testCase, status, 0, out)
            verifyInstallation(testCase)
        end
    end

    methods
        function verifyInstallation(testCase)
        % Verify installation by calling functions in matlab engine
        % Share this session and see if find_matlab can find it.
            sharedEngineName = string(matlab.engine.engineName);
            if (sharedEngineName == "")
                sharedEngineName = "MATLAB_tInstall";
                matlab.engine.shareEngine(sharedEngineName)
            end
            pySharedEngineName = string(py.matlab.engine.find_matlab());
            verifyEqual(testCase, pySharedEngineName, sharedEngineName)
            system("pip uninstall -y matlabengine")
        end
    end
end

