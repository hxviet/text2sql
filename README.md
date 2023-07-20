# text2sql

## Prerequisites
Install required modules and tools:
```sh
pip install -r requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz
python nltk_downloader.py
```

## Prepare data
Download [data](https://drive.google.com/file/d/19tsgBGAxpagULSl9r85IFKIZb4kyBGGu/view?usp=sharing) and [database](https://drive.google.com/file/d/1s4ItreFlTa8rUdzwVRmUR2Q9AHnxbNjo/view?usp=share_link) and then unzip them:
```sh
unzip data.zip
unzip database.zip
```

## SQLNet
### Train Models

```
  mkdir saved_models
  python train.py --dataset data/
```

### Test Models

```
python test.py --dataset data/ --output predicted_sql.txt
```

## RESDSQL
### Train Models

**RESDSQL-{Base}**
```sh
# Step1: preprocess dataset
sh scripts/train/text2sql/preprocess.sh
# Step2: train cross-encoder
sh scripts/train/text2sql/train_text2sql_schema_item_classifier.sh
# Step3: prepare text-to-sql training and development set for T5
sh scripts/train/text2sql/generate_text2sql_dataset.sh
# Step4: fine-tune T5-Base (RESDSQL-Base)
sh scripts/train/text2sql/train_text2sql_t5_base.sh
```

### Test Models

```sh
sh scripts/inference/infer_text2natsql.sh base spider
```

