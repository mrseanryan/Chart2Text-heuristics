function generate_summary()
{
    filepath=$1
    echo $filepath
    python3 ./src/generate_summary.py $filepath
    echo ""
}

echo == Series-based charts ==

generate_summary ./examples/dataset/data/1.csv
generate_summary ./examples/dataset/data/2.csv
generate_summary ./examples/dataset/data/3.csv
generate_summary ./examples/dataset/data/4.csv
generate_summary ./examples/dataset/data/5.csv

echo == Time-based charts ==
generate_summary ./examples/dataset/data/0.csv
generate_summary ./examples/dataset/data/101.csv
generate_summary ./examples/dataset/data/104.csv
generate_summary ./examples/dataset/data/105.csv
generate_summary ./examples/dataset/data/115.csv
