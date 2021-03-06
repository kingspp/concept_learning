import os
import pandas as pd
import numpy as np
from utils.utils import get_latent_vector_column
from config.common_path import get_encoded_csv_file


def encode_images(model, train_val_data_iterator, exp_config, epoch, dataset_type="train"):
    encoded_df = None
    while train_val_data_iterator.has_next(dataset_type):
        batch_images, batch_labels,_ = train_val_data_iterator.get_next_batch(dataset_type)
        if batch_images.shape[0] < exp_config.BATCH_SIZE:
            train_val_data_iterator.reset_counter(dataset_type)
            break

        mu, sigma, z = model.encode(batch_images)
        z_dim = z.shape[1]
        mean_col_names, sigma_col_names, z_col_names = get_latent_vector_column(z_dim)
        # TODO do this using numpy api
        labels = np.zeros(exp_config.BATCH_SIZE)
        i = 0
        for lbl in batch_labels:
            labels[i] = np.where(lbl == 1)[0][0]
            i += 1

        temp_df1 = pd.DataFrame(mu, columns=mean_col_names)
        temp_df2 = pd.DataFrame(sigma, columns=sigma_col_names)
        temp_df3 = pd.DataFrame(z, columns=z_col_names)
        temp_df = pd.concat([temp_df1, temp_df2, temp_df3], axis=1)
        temp_df["label"] = labels
        if encoded_df is not None:
            encoded_df = pd.concat([encoded_df, temp_df])
        else:
            encoded_df = temp_df
    print(exp_config.ANALYSIS_PATH)

    n_3 = exp_config.num_units[exp_config.num_decoder_layer - 2]
    n_2 = exp_config.num_units[exp_config.num_decoder_layer - 3]

    output_csv_file = get_encoded_csv_file(n_2, n_3, exp_config.Z_DIM, epoch, dataset_type)
    encoded_df.to_csv(os.path.join(exp_config.ANALYSIS_PATH, output_csv_file), index=False)
    return encoded_df
