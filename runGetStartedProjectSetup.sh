#!/bin/zsh

DEFAULT_PYTHON_VERSION=3.11.9
DEFAULT_APP_NAME="altruist-$DEFAULT_PYTHON_VERSION"
# region Functions
cleanup_oldVirtualEnv()
{
    echo "verify if old VirtualEnv exist for $DEFAULT_APP_NAME"
     if [ "$(pyenv virtualenvs | grep -c $DEFAULT_APP_NAME)" -gt 0 ]; then
        echo "$DEFAULT_APP_NAME found. Starting clean up phase"
    else
        echo "$DEFAULT_APP_NAME not found. Skipping cleanup phase"
        return        
    fi


    
    echo "cleanup old virtualenv for $DEFAULT_APP_NAME"

    #Step 1 - uninstall old virtualenv
    pyenv uninstall $DEFAULT_APP_NAME
    if [ $? -eq 0 ]; then
        echo "$DEFAULT_APP_NAME Uninstalled"
    else
        echo "Uninstall old virtualenv for $DEFAULT_APP_NAME failed - please check logs above."
        exit -1
    fi
}

install_UV(){
    echo "Installing UV"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ $? -eq 0 ]; then
        echo "UV Installed"
    else
        echo "Install UV failed - please check logs above."
        exit -1
    fi
}

install_Deps()
{
    echo "Installing dependencies"
    uv lock && uv sync
    if [ $? -eq 0 ]; then
        echo "All deps Installed"
    else
        echo "Install Deps failed - please check logs above."
        exit -1
    fi
}

config_VirtualEnv()
{
    echo "Configuring Python versions & virtual environment"
    #Step 1 - Python installation
    uv python install $DEFAULT_PYTHON_VERSION
    if [ $? -eq 0 ]; then
        echo "Python Installed"
    else
        echo "Config VirtualEnv failed - python version step, please check logs above."
        exit -1
    fi

    #Step 2 - virtualenv setup
    uv venv --python $DEFAULT_PYTHON_VERSION
    if [ $? -eq 0 ]; then
        echo "Virtual environment configured successfully"
    else
        echo "Config VirtualEnv failed - virtualenv setup step, please check logs above."
        exit -1
    fi

    #Step 3 - local setup
    uv python pin $DEFAULT_PYTHON_VERSION
    if [ $? -eq 0 ]; then
        echo "Python version pinned configured successfully"     
    else
        echo "Config VirtualEnv failed - Python version pin step, please check logs above."
        exit -1
    fi        
}
# endregion


# region Main body

#Step 1 - Install UV
install_UV

#Step 2 - Clean up old virtualenv
cleanup_oldVirtualEnv

#Step 3 - Install Deps
config_VirtualEnv


#step 4 - install
install_Deps

echo "Ready to develop"
exit 0


#endregion