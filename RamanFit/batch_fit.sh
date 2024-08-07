# chmod +x run_on_txt_files.sh

for file in *.txt
do
  # Run the Python script on each .txt file
  python start_fitting.py "$file"
done
