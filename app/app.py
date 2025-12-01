from shiny import App, render, ui, reactive
from shinyswatch import theme
import pandas as pd
import py3Dmol
# import py2Dmol
import os
from pathlib import Path

app_dir = Path(__file__).parent

## Load candidate data
candidate_df = pd.read_excel(app_dir / "../candidates.xlsx", sheet_name="Antibody Candidates")
haddock_df = pd.read_excel(app_dir / "../candidates.xlsx", sheet_name="HADDOCK3 Scores")

df = candidate_df.merge(
    haddock_df,
    on="antibody_id",
    suffixes=("", "_haddock")
)

## drop columns
df = df.drop(columns=[
    "antigen_id",
    "note_ids",
    "test_chotia_pass",
    "linker_seq",
    "franken_chain",
    "len_franken_chain",
    "len_lte_250",
    "status_folded_boltz2",
    "status_folded_franken_boltz2",
    "submitted_to_comp"
    ])

structure_dir = app_dir / "../data/candidates/structures_boltz2_frankenchain"


## py3Dmol Builder Function
def make_viewer_html(cif_path, ui_mode="dark"):
    with open(cif_path, "r") as f:
        cif_data = f.read()

    view = py3Dmol.view(width=250, height=250)
    view.addModel(cif_data, "cif")
    view.setStyle({'chain':'A'},{'cartoon': {'color': 'grey'}})
    view.setStyle({'chain':'B'},{'cartoon': {'color': 'blue'}})
    if ui_mode:
        view.setBackgroundColor('0x000000')
    else:
        view.setBackgroundColor('0xFFFFFF')
    view.zoomTo()
    return view._make_html()

## py2Dmol Builder Function
# def make_viewer_html(cif_path):
#     with open(cif_path, "r") as f:
#         cif_data = f.read()
#     view = py2Dmol.view(size=(250, 250))
#     view.add_pdb(cif_data, chains=['A', 'B'])
#     return view._display_viewer()


## UI
app_ui = ui.page_sidebar(  
    ui.sidebar(
        ui.input_dark_mode(id="dark_mode", value=True),
        ui.input_text("id_filter", "Search antibody ID", ""),
        ui.input_slider("score_filter", "HADDOCK3 Score", min=df["score"].min(), max=df["score"].max(), value=[df["score"].min(), 0]),  
        # bg="#f8f8f8"
        ),
    # ui.h2("Anti-Nipah Virus Glycoprotein G Fv Structures"),
    # ui.nav_control(ui.input_dark_mode()),
    ui.output_ui("cards_grid"),
    title = "Anti-Nipah Virus Glycoprotein G Fv Structures",
    theme = theme.darkly
) 


## Server
def server(input, output, session):

    @output
    @render.ui
    def cards_grid():
        ## Filter the dataframe by ID and HADDOCK3 Score
        search = input.id_filter().lower()
        filtered_df = df[
            (df["antibody_id"].str.lower().str.contains(search)) &
            (df["score"] >= input.score_filter()[0]) &
            (df["score"] <= input.score_filter()[1])
        ]

        card_list = []

        for _, row in filtered_df.iterrows():
            antibody_id = row["antibody_id"]
            cif_path = os.path.join(structure_dir, f"boltz_results_{antibody_id}/predictions/{antibody_id}/{antibody_id}_model_0.cif")

            if os.path.exists(cif_path):
                viewer_html = make_viewer_html(cif_path, ui_mode=input.dark_mode())
            else:
                viewer_html = "<b>No structure file found</b>"

            ## Build card
            card = ui.card(
                ui.card_header(f"{antibody_id}"),

                ui.HTML(viewer_html),

                ui.tags.div(
                    *(ui.tags.p(f"{col}: {row[col]}") for col in df.columns if col != "antibody_id")
                ),

                height="420px",
                style="padding: 10px;",
                full_screen=True
            )

            card_list.append(card)

        ## Responsive grid layout
        return ui.layout_column_wrap(
            *card_list,
            width="300px"
        )


app = App(app_ui, server)

