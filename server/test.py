import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import re

OPEN_FACE_EXTRACTED_FEATURES_FILE = 'frame_processed.csv'

# sns.set_style('white')

# Load data
df = pd.read_csv(os.path.join('samples', OPEN_FACE_EXTRACTED_FEATURES_FILE))
# Remove empty spaces in column names.
df.columns = [col.replace(" ", "") for col in df.columns]
# Print few values of data.
print(f"Max number of frames {df.face.max()}", f"\nTotal shape of dataframe {df.shape}")
print("Number of unique faces: ", len(df.face.unique()), "\nList of face's: ", df.face.unique())
print(df.head())
print(df.groupby('face').mean()['confidence'])

# Visualize the location of faces from the video
x_regex_pat = re.compile(r'^x_[0-9]+$')
y_regex_pat = re.compile(r'^y_[0-9]+$')
x_locs = df.columns[df.columns.str.contains(x_regex_pat)]
y_locs = df.columns[df.columns.str.contains(y_regex_pat)]
palette = sns.color_palette("RdBu_r", 1)

avg_face_df = pd.DataFrame({'x_locs':df[x_locs].mean(axis=1), 'y_locs':df[y_locs].mean(axis=1), 'face': df.face})
ax = sns.scatterplot(x='x_locs', y='y_locs', hue = 'face', data=avg_face_df, marker="+", palette=palette)
ax.set(xlim=[0, 1920], ylim=[1080,0], title="Before thresholding")

avg_face_df_conf = avg_face_df[df.confidence>=.80]
ax = sns.scatterplot(x='x_locs', y='y_locs', hue = 'face', data=avg_face_df_conf, marker="+", palette=palette[:3])
ax.set(xlim=[0, 1920], ylim=[1080,0], title="After thresholding")

# plt.show()

# Threshold data by 80%
df_clean = df[df.confidence>=.80]
# Plot all Action Unit time series.
au_regex_pat = re.compile(r'^AU[0-9]+_r$')
au_columns = df.columns[df.columns.str.contains(au_regex_pat)]
print("List of AU columns:", au_columns)
f,axes = plt.subplots(6, 3, figsize=(10,12), sharex=True, sharey=True)
axes = axes.flatten()
for au_ix, au_col in enumerate(au_columns):
    sns.lineplot(x='frame', y=au_col, hue='face', data=df_clean, ax=axes[au_ix])
    axes[au_ix].set(title=au_col, ylabel='Intensity')
    axes[au_ix].legend(loc=5)
plt.suptitle("AU intensity predictions by time for each face", y=1.02)
plt.tight_layout()

# Let's compare how much AU12 (smiling) activity occurs at similar times across people.
# df_clean.pivot(index='frame', columns='face', values='AU12_r').corr()
