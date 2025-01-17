import streamlit as st
from pydub import AudioSegment
# import pyglet ####
# from pyglet.media import Player####
import matplotlib.pyplot as plt
from youtubesearchpython import VideosSearch


 
from tempfile import NamedTemporaryFile
from recogniser_class import Recogniser
from fingerprint_class import Fingerprinting
from db_manager import DataBaseManager
import tempfile
import os,sys
import librosa
#from librosa.display import waveplot


#import sounddevice 
import numpy as np
import pandas as pd
#import soundfile as sf
# import librosa
# import librosa.display
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from waveform_class import Waveform
from microfon_class import Microfon
from waveform_class import Histogram

pagetitle = "Musikerkennung3000"

recogniser = Recogniser()
db_manager = DataBaseManager()
fingerprint_ = Fingerprinting

# def process_audio_for_histogram(audio_data, num_bins=10):
#     try:
#         # Convert audio data to numpy array
#         audio_array = np.array(audio_data)

#         # Calculate histogram
#         histogram, bin_edges = np.histogram(audio_array, bins=num_bins)
#         return histogram, bin_edges
#     except Exception as e:
#         st.error(f"Error processing audio data: {e}")
#         return None, None
    

def read_audio_file(audio_file_path, sr=44100):
    try:
        # Load audio file
        audio_data, _ = librosa.load(audio_file_path, sr=sr)
        return audio_data
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return None
    
def search_youtube(query):
    videosSearch = VideosSearch(query, limit=5)
    results = videosSearch.result()
    return results['result']
# def read_audio_file(audio_file_path, sr=44100):
#     try:
#         # Load audio file
#         audio_data, _ = librosa.load(audio_file_path, sr=sr)
#         return audio_data
#     except Exception as e:
#         print(f"Error reading audio file: {e}")
#         return None

# def process_audio_for_histogram(audio_data, num_bins=10):
#     # Converts audio data to numpy array (assuming mono audio)
#     audio_array = np.array(audio_data)
    
#     # Calculates histogram
#     histogram, bin_edges = np.histogram(audio_array, bins=num_bins)
    
#     return histogram, bin_edges


st.set_page_config(layout="wide", page_title=pagetitle, page_icon=":headphones:")
st.write(f"# {pagetitle}")
st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to", ["Teach Songs", "Recognize Songs", "About"])
col1, col2 = st.columns([0.5, 0.5])
with col1:
    if option == "Teach Songs":
        st.write("## Teach new Songs")
        with st.container(border=True):
            selected_file = st.file_uploader("Upload file to teach song", type=["mp3", "wav"], accept_multiple_files=False)
            if selected_file is not None:
                st.audio(selected_file, format='audio/wav')
            
        with st.form(key='teach_songs', border=True):
            title = st.text_input("Title")
            artist = st.text_input("Artist")
            album = st.text_input("Album")
            if st.form_submit_button('Add to Library'):          

                if selected_file is not None:
                
                    print(selected_file.name) #debug

                    temp_dir = tempfile.mkdtemp()
                    path = os.path.join(temp_dir, selected_file.name)
                    with open(path, "wb") as f:
                            f.write(selected_file.getvalue())
                    
                    fingerprint = Fingerprinting.fingerprint_file(path)
                    db_manager.store_song(title, fingerprint, artist, album)
                    
                    st.sidebar.success("Song added to library") # ich habe sidebar noch hinzugefuegt 
                    st.rerun()
                else:
                    st.error("Must upload a file to teach a song.")

    elif option == "Recognize Songs":
        st.write("## Recognize Songs from Snippet")
        with st.container(border=True):
            selected_snippet = st.file_uploader("Upload file to recognize song", type=["mp3", "wav"])
            if selected_snippet is not None:
                st.audio(selected_snippet, format='audio/wav')
            if st.button('Recognize'):
                #Insert logic to recognize song here
                #file has to be fingerprinted, hashes have to be compared to the database
                #if a match is found, the song has to be displayed
                #song info should be read from a separate table in the database
                #if no match is found, an error message has to be displayed
                print("Recognizing song...") #debug
                if selected_snippet:    
                    temp_dir = tempfile.mkdtemp()
                    path = os.path.join(temp_dir, selected_snippet.name)
                    with open(path, "wb") as f:
                            f.write(selected_snippet.getvalue())

                    recognition = recogniser.recognise_song(path)
                    print(recognition)
                    if recognition:
                        print("recognition", recognition)
                        st.success(f"Song {recognition['title']} recognized") 

                        with st.container(border=True):

                            st.write("## Music Library") 

                            # songs = db_manager.get_song_info(selected_snippet.file_id)
                            # print(f"songs: {songs}")  
                            st.write("### List of Songs")
                            # songs_table = []
                            # for song in songs:
                            # songs_table.append([recognition['title'], recognition['artist'], recognition['album']])
                            df = pd.DataFrame({
                                'Title': recognition['title'],
                                'Album': recognition['album'],
                                'Artist': recognition['artist']
                            }, index=[0])
                            st.table(df)

                        audio_data, sr = librosa.load(path)

                        # Plots the waveform
                        wv = Waveform(audio_data, sr)

                        # Plot waveform
                        wv.plot_waveform()
                        #  # Processes audio data for histogram
                        # histogram, bin_edges = process_audio_for_histogram(recognition, num_bins=10)
            
                        # # Plots histogram
                        # plt.bar(bin_edges[:-1], histogram, width=1)  # Plots histogram as bar chart

                        # plt.hist(recognition, bins=10)  # Creates the histogram
                        # plt.xlabel('X-axis label')
                        # plt.ylabel('Y-axis label')
                        # plt.title('Histogram')

                        # st.pyplot()
                        hstr = Histogram(selected_snippet)
                        histogram, bin_edges = hstr.process_audio_for_histogram(hstr.read_audio_file(path))
                        if histogram is not None and bin_edges is not None:
                            # Plot histogram
                            fig, ax = plt.subplots()
                            plt.bar(bin_edges[:-1], histogram, width=1)
                            plt.xlabel('Amplitude')
                            plt.ylabel('Frequency')
                            plt.title('Histogram of Recognized Song')
                            st.pyplot(fig)  # Display the histogram in Streamlit

                        videos = search_youtube(f"{recognition['title']} {recognition['album']} {recognition['artist']}")
                        for video in videos:
                            st.video(video['link'])

                    else:
                        st.error("We haven't found this song. Try to uplaod it to the database.")

        with st.container(border=True):
            st.write("## Recognize from recording")
            if st.button('Start Recording'):
                st.text("Recording for 10 seconds")
                temp_dir = tempfile.mkdtemp()
                path = os.path.join(temp_dir, "microfon_rec.mp3")
                microfon = Microfon(path, 10)
                microfon.recording_function()
                recognition = recogniser.recognise_song(path, threshold=20)
                if recognition:
                        print("recognition", recognition)
                        st.success(f"Song {recognition['title']} recognized") 

                        with st.container(border=True):

                            st.write("## Music Library") 
                            st.write("### List of Songs")
                            df = pd.DataFrame({
                                'Title': recognition['title'],
                                'Album': recognition['album'],
                                'Artist': recognition['artist']
                            }, index=[0])
                            st.table(df)

                        audio_data, sr = librosa.load(path)

                        # Plots the waveform
                        wv = Waveform(audio_data, sr)

                        # Plot waveform
                        wv.plot_waveform()

                        hstr = Histogram(selected_snippet)
                        histogram, bin_edges = hstr.process_audio_for_histogram(hstr.read_audio_file(path))
                        if histogram is not None and bin_edges is not None:
                            # Plot histogram
                            fig, ax = plt.subplots()
                            plt.bar(bin_edges[:-1], histogram, width=1)
                            plt.xlabel('Amplitude')
                            plt.ylabel('Frequency')
                            plt.title('Histogram of Recognized Song')
                            st.pyplot(fig)  # Display the histogram in Streamlit

                        videos = search_youtube(f"{recognition['title']} {recognition['album']} {recognition['artist']}")
                        for video in videos:
                            st.video(video['link'])

                else:
                    st.error("We haven't found this song. Try to uplaod it to the database.")
                #function to record audio from microphone and save it in recording.wav
                #st.write("Recording complete")
                # selected_audio = st.file_uploader("Upload file to recognize song", type=["mp3", "wav"])

                #microfon.recording_function(selected_audio,5)
                #st.audio(selected_audio, format='audio/wav')
                #insert logic to recognize song from recording here
                #file has to be fingerprinted, hashes have to be compared to the database
                #if a match is found, the song has to be displayed
                #song info should be read from a separate table in the database
                #if no match is found, an error message has to be displayed
                # print ("Recognizing song from recording...") #debug
                #if found:
                # print("Song recognized") #debug
                # plt.figure(figsize=(14, 5))
                # librosa.display.waveshow(y, sr=sr)
                # plt.xlabel('Zeit (s)')
                # plt.ylabel('Amplitude')
                # plt.title('Waveform des Musikstücks')
                # plt.show()
                #else:
                # print("Song ID not found in the database.")#debug

    else :
        st.write(f"## About {pagetitle}")
        st.write(f"{pagetitle} is a song recognition app that uses audio fingerprinting to recognize songs. It uses the Fingerprinting algorithm from the existing project abracadabra to generate hashes from audio files and stores them in a database. When a snippet is uploaded, it generates hashes from the snippet and compares them to the database to find a match. It can also record audio from the microphone and recognize songs from it.")
        st.write(f"{pagetitle} has been developed by Pavlo Slyvka, Vella Nedelcheva and Benedikt Reimeir as a final project for the course Softwaredesign at the MCI Innsbruck.")




