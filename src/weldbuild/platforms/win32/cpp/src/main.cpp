#include "precompiled.h"
#include "app.h"
#include <Python.h>

int main(int argc, char** argv) {
    try {
        App app;
        if(!app.check_install()) {
            app.install();
        }
    } catch(std::runtime_error e) {
        ::MessageBox(nullptr, e.what(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }
    
    std::filesystem::path const internal_path = std::filesystem::current_path();
    std::filesystem::path const app_path = internal_path / ".app";

#ifdef PYTHON_3_11
    PyStatus status;

    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);

    status = PyConfig_SetBytesString(&config, &config.program_name, "App");
    if (PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }

    config.module_search_paths_set = 1;
    config.site_import = 0;
    
    status = PyWideStringList_Append(&config.module_search_paths, (app_path / "site-packages").wstring().c_str());
    if(PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }

    status = PyWideStringList_Append(&config.module_search_paths, (app_path / "modules").wstring().c_str());
    if(PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }

    status = PyWideStringList_Append(&config.module_search_paths, (app_path / "stdlib.zip").wstring().c_str());
    if(PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }

    status = PyConfig_SetBytesString(&config, &config.executable, (app_path / "python.exe").string().c_str());
    if(PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }

    status = PyConfig_SetBytesString(&config, &config.run_filename, (app_path / "__boot__.pyc").string().c_str());
    if(PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }

    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        ::MessageBox(nullptr, std::format("{}", status.err_msg).c_str(), "App", MB_ICONERROR);
        return EXIT_FAILURE;
    }
    PyConfig_Clear(&config);
    return Py_RunMain();
#else
    return EXIT_FAILURE;
#endif
}
