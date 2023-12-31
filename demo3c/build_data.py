import os
import pandas as pd
import shutil

path = 'C:\\Users\\Administrator\\Desktop\\git_proj\\BGU_WP\\data\\LJSpeech'
lj_path = 'C:\\Users\\Administrator\\Desktop\\git_proj\\BGU_WP\\LJSpeech'
speakers = [f"LJ{i:03}" for i in range(1, 51)]
cosl = ['ID', 'Transcription', 'Normalized']
lj_df = pd.read_csv(lj_path + '\\metadata.csv', sep='|', header= None, names=cosl)
lj_df[['Sid', 'Rid']] = lj_df['ID'].str.split('-', expand=True)
lj_df = lj_df.drop('ID', axis=1)
print(lj_df.head())
# speakers = list(set(lj_df['Sid'].tolist()))
print(speakers)
wav_folder = 'C:\\Users\\Administrator\\Desktop\\git_proj\\BGU_WP\\LJSpeech\\wavs'
speaker_dataframes = {}
print(lj_df.columns)

for speaker in speakers:
    print(speaker)
    speaker_df = lj_df[lj_df['Sid'] == speaker]
    speaker_dataframes[speaker] = speaker_df
    speaker_folder = f'{path}\\{speaker}'
    print(speaker_folder)

    if not os.path.exists(speaker_folder):
        os.makedirs(speaker_folder)
    for index, row in speaker_df.iterrows():
        wav_file = f"{row['Sid']}-{row['Rid']}.wav"
        source_path = os.path.join(wav_folder, wav_file)
        # if os.path.exists(source_path):
        #     shutil.move(source_path, speaker_folder)

    df_path = f'{speaker_folder}\\{speaker}.csv'
    print(df_path)
    speaker_df.to_csv(df_path , index=False)