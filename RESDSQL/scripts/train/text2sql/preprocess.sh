set -e

# preprocess train_spider datasetz
if [ $1 = 'no-augment' ]
then 
    train_dataset_path="./data/spider/train_spider.json"
elif [ $1 = 'augment' ]
then
    train_dataset_path="./data/train_augment.json"
    # train_dataset_path="./data/refined_spider_aug.json"
else
    echo "The first arg must in [no-augment, augment]."
    exit
fi

python preprocessing.py \
    --mode "train" \
    --table_path "./data/spider/tables.json" \
    --input_dataset_path  $train_dataset_path\
    --output_dataset_path "./data/preprocessed_data/preprocessed_train_spider.json" \
    --db_path "./database" \
    --target_type "sql"

# preprocess dev dataset
python preprocessing.py \
    --mode "eval" \
    --table_path "./data/spider/tables.json" \
    --input_dataset_path "./data/spider/dev.json" \
    --output_dataset_path "./data/preprocessed_data/preprocessed_dev.json" \
    --db_path "./database"\
    --target_type "sql"