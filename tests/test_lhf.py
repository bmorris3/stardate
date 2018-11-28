import numpy as np
import pandas as pd
from stardate.lhf import lnprob
import stardate
from isochrones.mist import MIST_Isochrone
from isochrones import StarModel
mist = MIST_Isochrone()


def good_vs_bad(good_lnprob, nsamps):
    """
    Compare the likelihood of nsamps random parameter values against the
    likelihood of the true values.
    The true values should be higher.
    """
    for i in range(nsamps):
        bad_lnparams = good_lnparams*1
        bad_lnparams[0] = np.random.randn(1) * 10 + good_lnparams[0]  # eep
        bad_lnparams[1] = np.random.randn(1) * .5 + good_lnparams[1]  # age
        bad_lnparams[2] = np.random.randn(1) * .05 + good_lnparams[2]  # feh
        bad_lnparams[3] = np.random.randn(1) * .1 + good_lnparams[3]  # dist
        bad_lnprob = lnprob(bad_lnparams, *args)
        assert bad_lnprob[0] < good_lnprob[0], \
            "True parameters values must give a higher likelihood than" \
            " wrong values"


def test_lnprob_higher_likelihood_sun():
    """
    Make sure the likelihood goes down when the parameters are a worse fit.
    Test on Solar values.
    """
    iso_params = pd.DataFrame(dict({"teff": (5777, 10),
                                "logg": (4.44, .05),
                                "feh": (0., .001),
                                "parallax": (1., .01)}))  # mas

    # Set up the StarModel isochrones object.
    mod = StarModel(mist, **iso_params)
    args = [mod, 26., 1., False]  # the lnprob arguments]

    good_lnparams = [355, np.log10(4.56*1e9), 0., np.log(1000), 0.]
    good_lnprob = lnprob(good_lnparams, *args)
    good_vs_bad(good_lnprob, 10)



def test_lnprob_higher_likelihood_real():
    """
    The same test as above but for simulated data.
    """
    df = pd.read_csv("simulated_data.csv")
    teff_err = 25  # Kelvin
    logg_err = .05  # dex
    feh_err = .05  # dex
    jmag_err = .01 # mags
    hmag_err = .01  # mags
    kmag_err = .01  # mags
    parallax_err = .05  # milliarcseconds
    prot_err = 1  # Days
    BV_err = .01  # mags

    i = 0
    iso_params = pd.DataFrame(dict({"teff": (df.teff[i], 25),
                                    "logg": (df.logg[i], .05),
                                    "feh": (df.feh[i], .05),
                                    "jmag": (df.jmag[i], .01),
                                    "hmag": (df.hmag[i], .01),
                                    "kmag": (df.kmag[i], .01),
                                    "parallax": (df.parallax[i], .05)}))

    # Set up the StarModel isochrones object.
    mod = StarModel(mist, **iso_params)
    args = [mod, df.prot[i], 1, False]  # the lnprob arguments]
    good_lnparams = [df.eep.values[i], df.age.values[i], df.feh.values[i],
                     np.log(df.d_kpc.values[i]*1e3), df.Av.values[i]]
    good_lnprob = lnprob(good_lnparams, *args)
    good_vs_bad(good_lnprob, 10)


def test_likelihood_rotation():
    """
    Make sure that the lhf can cope with zeros, NaNs and None values for the
    rotation period.
    """
    iso_params = pd.DataFrame(dict({"teff": (5777, 10),
                                "logg": (4.44, .05),
                                "feh": (0., .001),
                                "parallax": (1., .01)}))  # mas
    # Set up the StarModel isochrones object.
    mod = StarModel(mist, **iso_params)
    lnparams = [355, np.log10(4.56*1e9), 0., np.log(1000), 0.]

    args = [mod, None, None, False]  # the lnprob arguments]
    none_lnprob = lnprob(lnparams, *args)

    args = [mod, np.nan, np.nan, False]  # the lnprob arguments]
    nan_lnprob = lnprob(lnparams, *args)

    args = [mod, 0., 0., False]  # the lnprob arguments]
    zero_lnprob = lnprob(lnparams, *args)

    args = [mod, 26., 1., True]  # the lnprob arguments]
    iso_lnprob = lnprob(lnparams, *args)

    args = [mod, 26., 1., False]  # the lnprob arguments]
    gyro_lnprob = lnprob(lnparams, *args)

    # check that gyro is switched off for all of these.
    assert iso_lnprob == none_lnprob
    assert iso_lnprob == nan_lnprob
    assert iso_lnprob == zero_lnprob

    # check that gyro on gives different lnprob
    assert gyro_lnprob != iso_lnprob

    giant_params = [450, np.log10(4.56*1e9), 0., np.log(1000), 0.]
    args = [mod, 26., 1., True]
    iso_giant_lnprob = lnprob(giant_params, *args)
    args = [mod, 26., 1., False]
    gyro_giant_lnprob = lnprob(giant_params, *args)

    # These should be the same because gyro is switched off for giants.
    assert iso_giant_lnprob == gyro_giant_lnprob

if __name__ == "__main__":
    test_lnprob_higher_likelihood_sun()
    test_lnprob_higher_likelihood_real()
    test_likelihood_rotation()

    """
    More test ideas

    1. test priors

    2. Test the MCMC somehow

    3. Test chronology somehow.
    """