from ydata_profiling import ProfileReport


def generate_report(dataframe, desc_file, output_file):
    """
    Génération d'un rapport html
    Parametres :
    data : dataframe
    desc_file : fichier de description des colonnes du dataframe
    out_pile : fichier rapport html
    """
    report = ProfileReport(dataframe, column_descriptions=desc_file)
    report.to_file(output_file)
