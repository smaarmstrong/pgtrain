# Convenience wrappers around ./bin/pgtrain, for when you just want to practise
# and not think about the command surface.
#
# New to PostgreSQL?  Let it teach you first:
#
#     make learn     # explains the next task (running real queries), then sets
#                    # up its database/workspace so you can try it
#     $EDITOR workspace/<domain>/<task>/solution.sql
#     make check     # grade it   (then `make learn` again for the next one)
#
# Already know the ropes?  Just practise:
#
#     make train     # picks what you should do next (new material or a review)
#     make check     # grade the task you're on
#
# `make train` decides on its own whether to give you new material (in a
# fundamentals-first order) or bring back something older for a spaced-
# repetition review. Everything here just forwards to ./bin/pgtrain — run
# `make help` for the list, or `./bin/pgtrain help` for the full CLI
# (start/psql/reset/solution, container control, and per-task ids).

PGTRAIN := ./bin/pgtrain
.DEFAULT_GOAL := help

.PHONY: help learn train next check solution list status cli

help: ; @printf 'pgtrain — just run one of:\n\n  make learn      teach the next task (real queries), then set it up to try\n  make train      pick the next task for you (new material, or a review)\n  make check      grade the task you are currently on\n  make solution   reveal the reference solution for it\n  make list       every task, grouped by domain, with your status\n  make status     your XP, streak and per-domain completion\n\nFull CLI (start/psql/reset a specific task by id, container control):  $(PGTRAIN) help\n'

learn:    ; @$(PGTRAIN) learn
train:    ; @$(PGTRAIN) train
next:     ; @$(PGTRAIN) train
check:    ; @$(PGTRAIN) check
solution: ; @$(PGTRAIN) solution
list:     ; @$(PGTRAIN) list
status:   ; @$(PGTRAIN) status
cli:      ; @$(PGTRAIN) help
