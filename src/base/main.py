# -*- coding: UTF-8 -*-
import argparse
import logging
import os
import shutil

import matplotlib.pyplot as plt
import pandas as pd
from pysptools.spectro import FeaturesConvexHullQuotient
from pysptools.spectro import SpectrumConvexHullQuotient

from src.config import settings

logger = logging.getLogger(__name__)


# Create function to save the spectra
def save_fig(fig_id, tight_layout=True, fig_extension="png", resolution=300):
    path = os.path.join(settings.OUTPUT_PATH / "plots", fig_id + "." + fig_extension)
    logger.info(f"Saving figure {fig_id}")
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)


def process_spectra(show_plots=True):
    """
    Process spectral data files.

    Args:
        show_plots: Whether to show plots during processing
    """
    path_folder = settings.OUTPUT_PATH / "data"
    path_results = settings.OUTPUT_PATH / "plots"

    logger.info(f"Processing spectra from: {path_folder}")
    logger.info(f"Saving results to: {path_results}")

    # Ensure results directory exists
    os.makedirs(path_results, exist_ok=True)

    # Find every file in the folder directory
    spectra_paths = [
        os.path.join(path_folder, f) for f in os.listdir(path_folder) if os.path.isfile(os.path.join(path_folder, f))
    ]
    spectra_paths.sort()

    if not spectra_paths:
        logger.error(f"No files found in {path_folder}")
        return

    # Get the name of the files
    names = [os.path.splitext(os.path.basename(x))[0] for x in spectra_paths]

    logger.info(f"Found {len(names)} spectra files: {', '.join(names)}")

    # Create a dictionary with all the spectra
    spectra = {}

    for i in range(len(names)):
        logger.info(f"Reading file: {spectra_paths[i]}")
        try:
            spectra[names[i]] = pd.read_table(
                spectra_paths[i], delim_whitespace=True, names=("Wvl", "Reflect. %"), skiprows=1
            )
        except Exception as e:
            logger.error(f"Error reading file {spectra_paths[i]}: {str(e)}")
            continue

    # Plot the spectra and save the figure
    logger.info("Plotting original spectra")

    for key, value in spectra.items():
        plt.figure()
        ax = plt.gca()
        spectra[key].plot(kind="line", x="Wvl", y="Reflect. %", ax=ax)
        plt.xlabel("Wavelength (nm)", fontsize=14)
        plt.xticks(size=14)
        plt.ylabel("Reflectance (%)", fontsize=14)
        plt.yticks(size=14)
        plt.title(key, fontsize=16, pad=10)
        ax.get_legend().remove()
        if show_plots:
            plt.show()
        save_fig(key)
        plt.pause(1)
        plt.close()

    # Change the parameters for plotting the figures
    params = {
        "legend.fontsize": "xx-large",
        "lines.linewidth": 3,
        "lines.markersize": 13,
        "figure.figsize": (14, 11),
        "figure.dpi": 300,
        "figure.titlesize": "xx-large",
        "axes.labelsize": "xx-large",
        "axes.titlesize": "xx-large",
        "axes.labelpad": 15,
        "axes.titlepad": 15,
        "xtick.labelsize": "x-large",
        "ytick.labelsize": "x-large",
    }
    plt.rcParams.update(params)

    # Remove the continnum
    logger.info("Removing continuum and extracting features")

    """ The FeaturesConvexHullQuotient function removes the convex-hull of the signal by hull quotient"""
    spectrum = list()
    wvl_list = list()

    for key, value in spectra.items():
        logger.info(f"Processing features for: {key}")

        pixel = value["Reflect. %"]
        wvl = value["Wvl"]
        spectrum = pixel.tolist()
        wvl_list = wvl.tolist()
        try:
            spectra_features = FeaturesConvexHullQuotient(spectrum=spectrum, wvl=wvl_list, baseline=0.99)
            # plot the extracted features
            spectra_features.plot(path=path_results, plot_name=key, feature="all")
            # plot side by side original and corrected spectrum
            # spectra_features.plot_convex_hull_quotient(path=path_results, plot_name=key + '_comparison')
            logger.info(f"Feature extraction completed for: {key}")
        except Exception as e:
            logger.error(f"Error extracting features for {key}: {str(e)}")

    # Get the statistics associated with each feature
    logger.info("Generating statistics for features")

    b = {}
    spectrum = list()
    wvl_list = list()
    full_data = pd.DataFrame()

    for key, value in spectra.items():
        logger.info(f"Generating statistics for: {key}")

        try:
            pixel = value["Reflect. %"]
            pixel = pixel / 100
            wvl = value["Wvl"]
            spectrum = pixel.tolist()
            wvl_list = wvl.tolist()
            spectra_features = FeaturesConvexHullQuotient(spectrum=spectrum, wvl=wvl_list, baseline=0.99)
            b = spectra_features.features_all
            b_stats = pd.DataFrame(b)
            is_keep = b_stats["state"] == "keep"
            b_stats_keep = b_stats[is_keep]
            csv_path = os.path.join(path_results, key + ".csv")
            b_stats_keep.to_csv(csv_path, sep=",", index=False)

            _data = b_stats_keep.loc[:]
            _data["filename"] = key
            _data["hx_1"] = _data["hx"].apply(lambda x: x[0] if x is not None else None)
            _data["hx_2"] = _data["hx"].apply(lambda x: x[1] if x is not None else None)
            _data["hy_1"] = _data["hy"].apply(lambda x: x[0] if x is not None else None)
            _data["hy_2"] = _data["hy"].apply(lambda x: x[1] if x is not None else None)
            _data["FWHM_x_1"] = _data["FWHM_x"].apply(lambda x: x[0] if x is not None else None)
            _data["FWHM_x_2"] = _data["FWHM_x"].apply(lambda x: x[1] if x is not None else None)
            _data["FWHM_y"] = _data["FWHM_y"].apply(lambda x: x[0] if x is not None else None)
            _data.drop(columns=["seq", "id", "state", "spectrum", "wvl", "crs", "hx", "hy", "FWHM_x"], inplace=True)
            full_data = pd.concat([full_data, _data], axis=0)
            logger.info(f"Statistics saved to: {csv_path}")
        except Exception as e:
            logger.error(f"Error generating statistics for {key}: {str(e)}")

    full_data.set_index("filename", inplace=True)
    full_data.to_excel(os.path.join(path_results, "results.xlsx"))
    # Export the continuum removed spectrum as *.txt, plot and save the spectra
    logger.info("Exporting continuum removed spectra")

    b = {}
    spectrum = list()
    wvl_list = list()
    plt.rcParams.update(plt.rcParamsDefault)
    for key, value in spectra.items():
        logger.info(f"Exporting continuum removed spectrum for: {key}")

        try:
            pixel = value["Reflect. %"]
            pixel = pixel / 100
            wvl = value["Wvl"]
            spectrum = pixel.tolist()
            wvl_list = wvl.tolist()
            spectra_remov = SpectrumConvexHullQuotient(spectrum=spectrum, wvl=wvl_list)
            conti_rem = spectra_remov.get_continuum_removed_spectrum()
            cont_corr = pd.DataFrame({"Reflectance": conti_rem})
            cont_corr.insert(0, "Wvl", wvl)
            cont_corr["Wvl"] = wvl
            txt_path = os.path.join(path_results, key + "_continuum_corr_spectra.txt")
            cont_corr.to_csv(txt_path, sep="\t", index=False, header=False)
            logger.info(f"Continuum removed spectrum saved to: {txt_path}")

            plt.figure()
            ax = plt.gca()
            cont_corr.plot(kind="line", color="g", x="Wvl", y="Reflectance", ax=ax)
            plt.xlabel("Wavelength (nm)", fontsize=14)
            plt.xticks(size=14)
            plt.ylabel("Continuum removed reflectance", fontsize=14)
            plt.yticks(size=14)
            plt.title(key, fontsize=16, pad=10)
            ax.get_legend().remove()
            if show_plots:
                plt.show()
            save_fig(key + "_continuum_removed")
            plt.pause(1)
            plt.close()
        except Exception as e:
            logger.error(f"Error exporting continuum removed spectrum for {key}: {str(e)}")

    logger.info("Processing completed successfully")

    return spectra


def _get_files(path):
    _files = []
    for file in os.listdir(path):
        if not file.startswith(".~lock."):
            _files.append(file)
    return _files


def generate_spectra():
    _thresholds = {
        "peak-1": (5500, 8000),
        "peak-2": (4600, 5540),
        "peak-3": (4310, 4788),
    }

    _path = settings.INPUT_PATH
    _filenames = [f for f in _get_files(_path) if f.endswith(".csv") or f.endswith(".CSV")]

    for _filename in _filenames:
        _df = pd.read_csv(os.path.join(_path, _filename))
        _df = _df.rename(columns={_df.columns[0]: "wavelength", _df.columns[1]: "reflectance"})
        _df = _df[["wavelength", "reflectance"]]
        _df = _df.apply(pd.to_numeric, errors="coerce")
        _df = _df.dropna()

        for _threshold, _limits in _thresholds.items():
            _peak_filename = f"{_filename.split('.')[0]}-{_threshold}"
            _df_peak = _df.loc[(_df["wavelength"] >= _limits[0]) & (_df["wavelength"] <= _limits[1])]
            _df_peak = _df_peak.reset_index(drop=True)
            _df_peak.rename(columns={"wavelength": "Wavelength", "reflectance": _peak_filename}, inplace=True)
            _df_peak.to_csv(
                os.path.join(settings.OUTPUT_PATH, "data", f"{_peak_filename}.txt"), sep="\t", index=False, header=True
            )


def _cleanup(path):
    if path.exists():
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")
    else:
        logger.warning(f"Path {path} does not exist. Cannot delete.")


def main():
    parser = argparse.ArgumentParser(description="Process NIR spectra files.")
    parser.add_argument("--no-plots", action="store_true", help="Do not show plots during processing", default=True)

    args = parser.parse_args()

    logger.info("Starting NIR spectra processing")

    try:
        _cleanup(settings.OUTPUT_PATH / "data")
        _cleanup(settings.OUTPUT_PATH / "plots")
        generate_spectra()
        process_spectra(show_plots=not args.no_plots)
        logger.info("Processing completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
