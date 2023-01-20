echo "Downloading examples images that match the dataset..."
pushd examples
mkdir images
cd images
git clone git@github.com:JasonObeid/Chart2TextImages.git
popd
echo "[done]"

