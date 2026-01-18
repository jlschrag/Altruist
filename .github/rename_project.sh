#!/usr/bin/env bash
while getopts t: flag
do
    case "${flag}" in
        t) template_project_name=${OPTARG};;
    esac
done

echo "template_project_name: $template_project_name";


echo "Renaming project..."
#rename file content
original_template_project_name_description="__template_project_name__"
for filename in $(git ls-files) 
do
    sed -i "s/$original_template_project_name_description/$template_project_name/gI" $filename
    echo "Renamed $filename"
done


#rename file name
for filename in $(git ls-files | grep -i "__template_project_name__")
do
    newname=$(echo $filename | sed "s/__template_project_name__/$template_project_name/gI")
    git mv $filename $newname
    echo "Renamed $filename to $newname"
done

# This command runs only once on GHA.
rm -f .github/workflows/main.yml
rm -f .github/template.yml
rm -f .github/rename_project.sh