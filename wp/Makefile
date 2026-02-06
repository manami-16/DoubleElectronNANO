PYTHON = python3
DATASET = VBF  ## VBF or Inclusive
PLOT_OUTDIR = /eos/user/m/mkanemur/WebEOS/WorkingPoint  ## change it to yours

wp:
	$(PYTHON) workflows/derive_wp.py --dataset $(DATASET) --outdir $(PLOT_OUTDIR)

plots:
	$(PYTHON) workflows/make_plots.py --dataset $(DATASET) --outdir $(PLOT_OUTDIR)

all: wp plots