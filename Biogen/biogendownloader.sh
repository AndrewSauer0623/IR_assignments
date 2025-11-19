#!/bin/zsh
set -e
OUTPUT_DIR=${1:-"./biogen_data_sample"}
PUBMED_BASE_URL="https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"
PMID_JSON_URL="https://dmice.ohsu.edu/trec-biogen/static/pubmed_ids_last_20_years.json.gz"

echo "==> Creating output directory: $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/pubmed_baseline"
cd "$OUTPUT_DIR"

# Download and extract PubMed IDs JSON
echo "==> Downloading PubMed ID list JSON..."
curl -L --progress-bar -o "pubmed_ids_last_20_years.json.gz" "$PMID_JSON_URL"
gunzip -f "pubmed_ids_last_20_years.json.gz"
echo "JSON extracted to: $OUTPUT_DIR/pubmed_ids_last_20_years.json"

# Fetch file listing from PubMed baseline
echo "==> Fetching list of PubMed baseline files..."
curl -s "$PUBMED_BASE_URL" | grep -Eo 'pubmed[0-9]+n[0-9]+\.xml\.gz' | sort | uniq | head -n 150 > baseline_sample_list.txt

if [[ ! -s baseline_sample_list.txt ]]; then
  echo "⚠️  No files found — check the PubMed FTP link or your network."
  exit 1
fi

echo "==> Downloading first 10 baseline XML files..."
cat baseline_sample_list.txt

# Download files with progress bars
while read -r file; do
  echo ""
  echo "📦 Downloading $file..."
  curl -L --progress-bar -o "pubmed_baseline/$file" "${PUBMED_BASE_URL}${file}"
done < baseline_sample_list.txt

# Extract the files
echo ""
echo "==> Extracting downloaded .gz files..."
for gzfile in pubmed_baseline/*.gz; do
  if [[ -f "$gzfile" ]]; then
    echo "🧩 Extracting $(basename "$gzfile")"
    gunzip -f "$gzfile"
  fi
done


