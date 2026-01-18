#!/bin/zsh

#region aux functions
function usage() {
  echo "Usage: $0 [OPTION]..." >&2
  echo "" >&2
  echo "In case of no option all the profiles will be started..." >&2
  echo "" >&2
  echo "-d, -dependencies, --dependencies                                       install and start dependencies profile only" >&2
  echo "-h, -help, --help                                                       help" >&2
  echo "-p profilename, -profile profilename,  --profile profilename            install and start profile. Double-quoted comma-separated non-empty String with the list of profiles" >&2
  echo "-s [profilename], -stop [profilename],  --stop [profilename]            stop profiles. profilename is optional and if not pass all profiles will be stopped" >&2
  echo "" >&2
}

function concatProfileNames() {
  local result=""
  local profileTempList=""
  IFS="," read -r -a profileTempList <<< "$1"

  local needAppendNextIndex="${#profileTempList[@]}"
  for item in "${profileTempList[@]}"; do
    result="$result$item "
    : $((--needAppendNextIndex))
    if [ $needAppendNextIndex -ge 1 ]; then
      result="$result --profile "
    fi
  done

  echo $result
}

function exportVariables() {
  local VERSION=$(cat ./version)
  local versionArray=()
  IFS="." read -r -a versionArray <<< "$VERSION"

  if [[ ${#versionArray[@]} -ne 3 ]]; then
    echo 'version file is not well format. expected: 1.0.0' >&2
    echo 'actual: '$VERSION >&2
    exit 1
  fi

  export MAJOR_VERSION=${versionArray[0]}
  export MINOR_VERSION=${versionArray[1]}
  export PATCH_VERSION=${versionArray[2]}
  export GIT_COMMIT=$(git rev-parse --short HEAD)
}
#endregion


#region argumentsValidation

if [[ $# -gt 2 ]]; then
  echo 'Too many arguments, expecting one or none.' >&2
  usage
  exit 1
fi

profileNames=""
action="defaultStop"

if [[ $# == 0 ]]; then
  echo "starting all profiles"
  profileNames="*"
  action="start"
else
  case "$1" in
  -d| -dependencies| --dependencies)
    if [[ $# -gt 1 ]]; then
      echo "Invalid option: $*. Option d does not accept other parameters." >&2
      usage
      exit 1
    else
      profileNames="dependency_only"
      action="start"
    fi
    ;;
  -h| -help| --help)
    usage
    exit 1
    ;;
  -p| -profile| --profile)
    if [[ $# -ne 2 ]]; then
      echo "Invalid option: $*. Option P only accept one parameters with the profile name as string and comma separeted." >&2
      usage
      exit 1
    else
      echo "starting profiles: $2"
      profileNames=$(concatProfileNames $2)
      action="start"
    fi
    ;;
  -s| -stop| --stop)
    if [[ $# -lt 1 || $# -gt 3 ]]; then
      echo "Invalid option: $*. Option S accepts zero or one parameter with the profile name as string and comma separeted." >&2
      usage
      exit 1
    else
      if [ -z "$2" ]; then
        echo "stop profiles: *"
        profileNames="*"
      else
        echo "stop profiles: $2"
        profileNames=$(concatProfileNames $2)
      fi
    fi
    ;;
  *)
    echo "Invalid option: $*" >&2
    usage
    exit 1
    ;;
  esac
fi

#endregion

#region Main Script

if [ -z "$profileNames" ]; then
  echo "No Profile set. script issue."
  exit 1
fi

echo Stopping docker compose with profile "$profileNames"
docker compose --profile "$profileNames" down
if [ $? -ne 0 ]; then
  echo "Docker compose failled to shutdown services, please review logs."
  exit 1
fi

if [ "$action" = "start" ]; then
  echo Starting docker-compose with profile "$profileNames"
  exportVariables
  docker compose --profile "$profileNames" up -d --build
  if [ $? -ne 0 ]; then
    echo "Docker compose failled to start services, please review logs."
    exit 1
  fi
fi

echo "Docker compose finished successfully."
exit 0
#endregion
