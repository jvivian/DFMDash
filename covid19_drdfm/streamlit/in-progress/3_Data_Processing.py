import streamlit as st
import pandas as pd


def main():
    st.title("CSV Metadata Selector")

    # File upload
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Display the DataFrame
        st.dataframe(df)

        # Select metadata columns
        st.subheader("Select Metadata Columns")
        metadata_columns = st.multiselect("Select columns", df.columns)

        # Process the selected metadata columns
        if st.button("Process"):
            metadata_df = df[metadata_columns]
            st.dataframe(metadata_df)


if __name__ == "__main__":
    main()
