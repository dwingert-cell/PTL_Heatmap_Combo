import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
from Cable import Cable
from Heatmap import display_matrix  
from uploadData import process_csv
import os
from Tesla import Tesla
from Paradise import Paradise
import numpy as np

import plotly.express as px



import os
import io
import zipfile

import streamlit as st
import pandas as pd

def has_data(cables, cable_type, test_type: str) -> bool:
    """
    Return True if 'cables' has data for the given cable_type and test_type.
    Adjust logic based on your actual data structure.
    """
    if cables is None:
        return False

    for cable in cables.values():
        if(cable.type == cable_type):
            if(test_type == "1s"):
                if(cable.leakage_1s is not None):
                    return True
            elif(test_type == "leakage"):
                if(cable.leakage is not None):
                    return True
    return False



def _nice_label(attr_name: str) -> str:
    return attr_name.replace("_", " ").title()

def generate_max_leakage_histogram(cables, cable_type, test_type):
    maximum_leakage_data = []
    for cable in cables.values():
        if(cable.type == cable_type):
            if(test_type == "1s"):
                cable_data = cable.leakage_1s
            elif(test_type == "leakage"):
                cable_data = cable.leakage   
            else:
                continue
            
            if cable_data is None or cable_data.empty:
                continue
            
            if isinstance(cable_data, pd.DataFrame):
                print(cable_data)
                max_leakage = cable_data["Measured_pA"].to_numpy().max()
            else:  # Series
                max_leakage = cable_data.max()

            maximum_leakage_data.append(max_leakage)

    max_leakage_df = pd.DataFrame(
            {"max_leakage": maximum_leakage_data}
        )
    
    
    bins = list(range(0, 10001, 200))  # 0, 200, 400, ..., 10000
    labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)] + ["10,000+ pA"]

    max_leakage_df["bin"] = pd.cut(max_leakage_df["max_leakage"], bins=bins+[np.inf], labels=labels, right=False)
    


    fig = px.histogram(
            max_leakage_df,
            x="bin",
            title=f"Max Leakage Histogram ({cable_type}, {test_type})",
            labels={"bin": "Leakage Range"},
            text_auto=True,
            
            category_orders={"bin": labels}  # <-- Force correct order

        )


    fig.update_layout(
        xaxis_title="Maximum Leakage",
     template="plotly_white"
    )
    

    fig.add_vline(
        x=labels.index("2000-2200"),  # Position near the 2000 bin
        line_dash="dash",
        line_color="red",
        annotation_text="2000 pA",
        annotation_position="top right"
    )


    return max_leakage_df, fig


def generate_all_leakage_histogram(cables, cable_type, test_type):
    leakage_data = []
    for cable in cables.values():
        if(cable.type == cable_type):
            if(test_type == "1s"):
                cable_data = cable.leakage_1s
            elif(test_type == "leakage"):
                cable_data = cable.leakage   
            else:
                continue
            
            if cable_data is None or cable_data.empty:
                continue
            
            if isinstance(cable_data, pd.DataFrame):
                #extract all the cable leakage values 
                values = cable_data.to_numpy().flatten()
                values = pd.to_numeric(values, errors='coerce')
                values = values[~np.isnan(values)]
                leakage_data.extend(values)
            

            else:  # Series

                values = cable_data.dropna().values
                leakage_data.extend(values)

            #append cable_data to leakage_data 
    leakage_df = pd.DataFrame(
            {"leakage_data": leakage_data}
        )
    bins = list(range(0, 10001, 200))  # 0, 200, 400, ..., 10000
    labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)] + ["10,000+ pA"]

    leakage_df["bin"] = pd.cut(leakage_df["leakage_data"], bins=bins+[np.inf], labels=labels, right=False)

    fig = px.histogram(
        leakage_df,
        x="bin",
        labels={"bin": "Leakage Range"},
        text_auto=True,
        category_orders={"bin": labels},  # <-- Force correct order
        title=f"Leakage Histogram ({cable_type}, {test_type})"
    )

    fig.update_layout(
        xaxis_title="Leakage",

     template="plotly_white"
    )
    fig.add_vline(
        x=labels.index("2000-2200"),  # Position near the 2000 bin
        line_dash="dash",
        line_color="red",
        annotation_text="2000 pA",
        annotation_position="top right"
    )

    return leakage_df, fig


def render_histogram_buttons(cables, cable_type: str, group_key: str):
    """
    Render a row of 4 histogram/action buttons for a specific cable type.
    """
    st.markdown(f"#### {cable_type} – Histograms")

    has_max_leakage      = has_data(cables, cable_type, test_type="leakage")
    has_all_points       = has_data(cables, cable_type, test_type="leakage")
    has_max_leakage_1s   = has_data(cables, cable_type, test_type="1s")
    has_all_points_1s    = has_data(cables, cable_type, test_type="1s")

    # 4 equally spaced columns for 4 histogram buttons
    h1, h2, h3, h4 = st.columns(4)

    with h1:
        chart_slot = st.empty()
        clicked = st.button("Max Leakage", key=f"{group_key}_hist_max_leakage", use_container_width=True, disabled = not has_max_leakage)
        if clicked:
            df, fig = generate_max_leakage_histogram(cables=cables, cable_type=cable_type, test_type = "leakage")
            st.session_state[f"{group_key}_fig_1"] = fig
        if f"{group_key}_fig_1" in st.session_state:
            chart_slot.plotly_chart(
                st.session_state[f"{group_key}_fig_1"],
                use_container_width=True
            )


    with h2:
        chart_slot = st.empty()
        if st.button("All Test Points", key=f"{group_key}_hist_all_points", use_container_width=True, disabled = not has_all_points):
            df, fig = generate_all_leakage_histogram(cables=cables, cable_type=cable_type, test_type = "leakage")
            
            st.session_state[f"{group_key}_fig_2"] = fig

        if f"{group_key}_fig_2" in st.session_state:
            chart_slot.plotly_chart(
                st.session_state[f"{group_key}_fig_2"],
                use_container_width=True
            )


    with h3:
        chart_slot = st.empty()
        if st.button("Max Leakage 1s", key=f"{group_key}_hist_leakage_1s", use_container_width=True, disabled=not has_max_leakage_1s):
            df, fig = generate_max_leakage_histogram(cables=cables, cable_type=cable_type, test_type = "1s")
            
            st.session_state[f"{group_key}_fig_3"] = fig

        if f"{group_key}_fig_3" in st.session_state:
            chart_slot.plotly_chart(
                st.session_state[f"{group_key}_fig_3"],
                use_container_width=True
            )


    with h4:
        chart_slot = st.empty()
        if st.button("All Test Points 1s", key=f"{group_key}_hist_resistance", use_container_width=True, disabled=not has_all_points_1s):
            df, fig = generate_all_leakage_histogram(cables=cables, cable_type=cable_type, test_type = "1s")
            
            st.session_state[f"{group_key}_fig_4"] = fig

        if f"{group_key}_fig_4" in st.session_state:
            chart_slot.plotly_chart(
                st.session_state[f"{group_key}_fig_4"],
                use_container_width=True
            )




def render_csv_group(cables, cable_type: str, attr_names: list, group_key: str):
    """
    Render your existing group of 6 CSV action buttons.
    If you already have render_group_of_six_buttons, you can just call it here.
    """
    st.markdown(f"#### {cable_type} – Download CSV")
    # If you already defined render_group_of_six_buttons, call that:
    render_group_of_six_buttons(
        cables,
        cable_type=cable_type,
        attr_names=attr_names,
        group_key=group_key,
    )


def render_group_of_six_buttons(
    cables: dict,
    cable_type: str,
    attr_names: list,
    group_key: str,
):
    """
    Renders 6 buttons (2 rows × 3 cols).
    Each button:
      • starts as "Generate <attr>"
      • becomes "Download <attr>" after generation
    """

    # Ensure fixed layout
    attr_names = (attr_names + [None] * 6)[:6]

    def has_data(attr):
        if attr is None:
            return False
        for cable in cables.values():
            if cable.type == cable_type:
                df = getattr(cable, attr, None)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    return True
        return False

    rows = [st.columns(3), st.columns(3)]

    for i, attr in enumerate(attr_names):
        col = rows[i // 3][i % 3]

        if attr is None:
            col.empty()
            continue

        nice_label = attr.replace("_", " ").title()
        state_key = f"{group_key}_{attr}"
        csv_key   = f"csv_{state_key}"
        ready_key = f"ready_{state_key}"

        disabled = not has_data(attr)
        if st.session_state.get(ready_key, False):
            col.download_button(
                label=f"Download {nice_label}",
                data=st.session_state[csv_key],
                file_name=f"{cable_type.lower()}_{attr}.csv",
                mime="text/csv",
                key=f"dl_{state_key}",
            )
        else:
            if col.button(
                label=f"Generate {nice_label}",
                disabled=disabled,
                key=f"gen_{state_key}",
            ):
                df, err = build_master_dataframe(
                    cables,
                    cable_type=cable_type,
                    attr_name=attr,
                )

                if err:
                    col.warning(err)
                else:
                    buf = io.StringIO()
                    df.to_csv(buf, index=False)
                    st.session_state[csv_key] = buf.getvalue()
                    st.session_state[ready_key] = True





def build_master_dataframe(
    cables: dict,
    cable_type: str,
    attr_name: str,
):
    """
    Build a master DataFrame for the given cable type and data attribute.
    - Deduplicates each cable's DataFrame by taking the max per key (first column).
    - Merges all cables on the shared first column via outer join.
    - If duplicates remain, collapses them by taking column-wise max per key.
    """

    dfs = []

    for cable in cables.values():
        if getattr(cable, "type", None) != cable_type:
            continue

        df = getattr(cable, attr_name, None)
        if df is None or df.empty:
            continue

        # Work with first two columns: [shared_key, measurement]
        tmp = df.iloc[:, :2].copy()
        shared_col = tmp.columns[0]
        meas_col   = tmp.columns[1]

        # Ensure measurement is numeric for max calculation
        tmp[meas_col] = pd.to_numeric(tmp[meas_col], errors="coerce")

        # 1) Deduplicate within this cable: max per key
        tmp = (
            tmp.groupby(shared_col, as_index=False)
               .agg({meas_col: "max"})
        )

        # 2) Rename measurement column to the cable's serial number
        tmp = tmp.rename(columns={meas_col: cable.serial_number})

        dfs.append(tmp)

    if not dfs:
        return None, f"No {attr_name} data found for {cable_type} cables."

    # Use the first DataFrame's first column name as the join key
    master_df = dfs[0].copy()
    key_col = master_df.columns[0]

    # 3) Merge all cables on shared key
    for df_i in dfs[1:]:
        # Align key column name if differs
        if df_i.columns[0] != key_col:
            df_i = df_i.rename(columns={df_i.columns[0]: key_col})
        master_df = master_df.merge(df_i, on=key_col, how="outer")

    # 4) If any duplicate keys exist post-merge, collapse by max per column
    # Convert all measurement columns to numeric for max; leave key untouched
    meas_cols = [c for c in master_df.columns if c != key_col]
    for c in meas_cols:
        master_df[c] = pd.to_numeric(master_df[c], errors="coerce")

    master_df = (
        master_df.groupby(key_col, as_index=False)
                 .max(numeric_only=True)
    )

    # 5) Sort by the shared key (numeric if possible)
    master_df[key_col] = pd.to_numeric(master_df[key_col], errors="ignore")
    master_df = master_df.sort_values(by=key_col)

    return master_df, None


def build_zip_for_cable(cable, base_map=None, temp_root="."):
    """
    Returns (zip_buffer, zip_name) if success, else (None, error_msg).
    Expects folder structure:
      TeslaTemp/<serial_number>/...
      ParadiseTemp/<serial_number>/...
    """
    if base_map is None:
        base_map = {"Tesla": "teslaTemp", "Paradise": "paradiseTemp"}

    base_dir = base_map.get(cable.type)
    if not base_dir:
        return None, f"Unknown cable_type '{cable.type}'"
    

    if not cable.serial_number:
        return None, "Missing serial number"
    
    length_folder = f"{cable.length}"
    target_dir = os.path.join(
        temp_root,
        base_dir,
        length_folder,
        str(cable.serial_number)
    )
    
    if not os.path.isdir(target_dir):
        return None, f"Folder not found: {target_dir}"

    # Check folder is not empty
    has_files = any(
        len(files) > 0 for _, _, files in os.walk(target_dir)
    )
    if not has_files:
        return None, f"No files in {target_dir}"

    # Build ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(target_dir):
            for fname in files:
                abs_path = os.path.join(root, fname)
                # Make paths inside the zip start at <serial_number>/...
                rel_from_sn = os.path.relpath(abs_path, start=target_dir)
                arcname = os.path.join(str(cable.serial_number), rel_from_sn)
                zf.write(abs_path, arcname=arcname)

    zip_buffer.seek(0)
    zip_name = f"{cable.serial_number}_data.zip"
    return zip_buffer, zip_name


def create_cable(cable_type, cable_length, serial_number):
    if cable_type == "Tesla":
        return Tesla(cable_type, cable_length, serial_number)
    elif cable_type == "Paradise":
        return Paradise(cable_type, cable_length, serial_number)
    else:
        raise ValueError(f"Unknown cable type: {cable_type}")


st.set_page_config(
    layout="wide"
)

st.title("PTL Cable Data Analysis")

os.makedirs("temp", exist_ok=True)
uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)
cables = {}

pattern = re.compile(r"(?<![A-Za-z0-9])0[0-4][A-Za-z0-9]{8}(?![A-Za-z0-9])", re.IGNORECASE)

if uploaded_files:
    for uploaded_file in uploaded_files:
        serial_number = "Unknown"
            
        target_text = uploaded_file.name

        match = pattern.search(target_text)  # or uploaded_file.name
        if match:
            serial_number = match.group()
            if len(serial_number) >= 2:
                    first_two_digits = serial_number[:2]
                    second_digit = first_two_digits[1]          
                    if second_digit == "0":
                        cable_type = "Paradise"
                        cable_length = 11
                    elif second_digit == "1":
                        cable_type = "Paradise"
                        cable_length = 15
                    elif second_digit == "3":
                        cable_type = "Tesla"
                        cable_length = 11
                    elif second_digit == "4":
                        cable_type = "Tesla"
                        cable_length = 15

            
            if serial_number in cables:
                cable = cables[serial_number]
            else:
                cable = create_cable(cable_type, cable_length, serial_number)
                cables[serial_number] = cable

            process_csv(cable, uploaded_file)
    
    
    TESLA_ATTRS = [
        "leakage", "leakage_1s", "resistance",
        "inv_resistance", "continuity", "inv_continuity"
    ]

    PARADISE_ATTRS = [
        "leakage", "leakage_1s", "resistance",
        "inv_resistance", "continuity", "inv_continuity"
    ]

    st.subheader("Master CSV Files")

    # -----------------------
    # TESLA SECTION
    # -----------------------
    st.markdown("### Tesla")

    # 4 histogram action buttons (row)
    render_histogram_buttons(
        cables=cables,
        cable_type="Tesla",
        group_key="tesla"
    )

    # 6 CSV buttons (your existing group)
    render_csv_group(
        cables=cables,
        cable_type="Tesla",
        attr_names=TESLA_ATTRS,
        group_key="tesla"
    )

    st.divider()

    # -----------------------
    # PARADISE SECTION
    # -----------------------
    st.markdown("### Paradise")

    # 4 histogram action buttons (row)
    render_histogram_buttons(
        cables=cables,
        cable_type="Paradise",
        group_key="paradise"
    )

    # 6 CSV buttons (your existing group)
    render_csv_group(
        cables=cables,
        cable_type="Paradise",
        attr_names=PARADISE_ATTRS,
        group_key="paradise"
    )

    st.divider()


    
    COL_LAYOUT = [1, 1, 1, 5, 5, 2]
    st.subheader("Processed Cables")


    disabled_leakage = getattr(cable, "leakage", None) is None
    disabled_1s = getattr(cable, "leakage_1s", None) is None

    header_cols = st.columns(COL_LAYOUT)
    header_cols[0].markdown("**Serial Number**")
    header_cols[1].markdown("**Cable Type**")
    header_cols[2].markdown("**Length (in)**")
    header_cols[3].markdown("**Leakage Heatmap**", disabled_leakage)
    header_cols[4].markdown("**1s Leakage Heatmap**", disabled_1s)
    header_cols[5].markdown("**Download CSVs**")

    for cable in cables.values():
        cols = st.columns(COL_LAYOUT)

        cols[0].markdown(cable.serial_number)
        cols[1].markdown(cable.type)
        cols[2].markdown(cable.length)
        
        show_key_leak = f"show_leakage_{cable.serial_number}"
        show_key_1s   = f"show_1s_{cable.serial_number}"
        
        has_leakage   = isinstance(getattr(cable, "leakage", None), pd.DataFrame) and not getattr(cable, "leakage").empty
        has_leakage_1s = isinstance(getattr(cable, "leakage_1s", None), pd.DataFrame) and not getattr(cable, "leakage_1s").empty


        if show_key_leak not in st.session_state:
            st.session_state[show_key_leak] = False
        if show_key_1s not in st.session_state:
            st.session_state[show_key_1s] = False

        if cols[3].button(
            "Generate",
            key=f"leakage_{cable.serial_number}",
            disabled=not has_leakage or st.session_state[show_key_leak]
        ):
            st.session_state[show_key_leak] = True
            
        if cols[4].button(
            "Generate",
            key=f"leakage_1s_{cable.serial_number}",
            disabled=not has_leakage_1s or st.session_state[show_key_1s]
        ):
            st.session_state[show_key_1s] = True
        
        if st.session_state[show_key_leak]:
            fig = cable.draw_heatmap_plotly(matrix_type = "leakage")
            fig_leak, ax_leak = cable.draw_heatmap("leakage")
            cols[3].plotly_chart(fig, use_container_width=True)
            #cols[3].pyplot(fig_leak, use_container_width=True)


        if st.session_state[show_key_1s]:
            
            fig = cable.draw_heatmap_plotly(matrix_type="1s")
            fig_1s, ax_1s = cable.draw_heatmap("1s")
            cols[4].plotly_chart(fig, use_container_width=True)
            #cols[4].pyplot(fig_1s, use_container_width=True)

        zip_buf, zip_name_or_err = build_zip_for_cable(
            cable,
            base_map={"Tesla": "teslaTemp", "Paradise": "paradiseTemp"},
            temp_root="." 
        )

        if zip_buf:
            cols[5].download_button(
                label="Download ZIP",
                data=zip_buf,
                file_name=zip_name_or_err,   # this is the zip_name
                mime="application/zip",
                key=f"download_{cable.serial_number}",
            )

        else:
                # Show a disabled button with a tooltip-like note
                cols[5].button(
                    "Download ZIP",
                    key=f"download_disabled_{cable.serial_number}",
                    disabled=True,
                    help=str(zip_name_or_err)  # this is the error message
                )


