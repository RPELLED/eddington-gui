# pylint: disable=too-many-instance-attributes,too-many-public-methods
"""Box for setting up plot configuration for the output graphs."""
from typing import Optional

import toga
from eddington import EddingtonException, FigureBuilder, to_relevant_precision_string
from eddington.interval import Interval
from eddington.plot.figure import Figure
from matplotlib.ticker import FuncFormatter, NullLocator
from toga.style import Pack
from toga.style.pack import COLUMN, HIDDEN, VISIBLE
from toga.validators import Number

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LABEL_WIDTH, LONG_INPUT_WIDTH, SMALL_PADDING

EDDINGTON_FORMATTER = FuncFormatter(lambda y, _: to_relevant_precision_string(y))
NULL_LOCATOR = NullLocator()


class PlotConfigurationBox(EddingtonBox):
    """Visual box to create plot configuration."""

    __title_input: toga.TextInput
    __xlabel_input: toga.TextInput
    __ylabel_input: toga.TextInput
    __grid_switch: toga.Switch
    __legend_switch: Optional[toga.Switch]
    __x_domain_switch: toga.Switch
    __x_min_title: toga.Label
    __x_min_input: toga.TextInput
    __x_max_title: toga.Label
    __x_max_input: toga.TextInput
    __x_log_scale: toga.Switch
    __y_log_scale: toga.Switch

    __has_legend: bool
    __base_name: Optional[str]
    __xcolumn: Optional[str]
    __ycolumn: Optional[str]

    def __init__(self, additional_instructions, suffix, has_legend=True):
        """Initialize box."""
        super().__init__(style=Pack(direction=COLUMN))
        self.__base_name = None
        self.__ycolumn = None
        self.__xcolumn = None

        self.additional_instructions = additional_instructions
        self.suffix = suffix
        self.__title_input = self.__add_column_option("Title:")
        self.__x_log_scale = toga.Switch(
            text="X log scale", style=Pack(padding_left=SMALL_PADDING)
        )
        self.__y_log_scale = toga.Switch(
            text="Y log scale", style=Pack(padding_left=SMALL_PADDING)
        )
        self.__xlabel_input = self.__add_column_option("X label:", self.__x_log_scale)
        self.__ylabel_input = self.__add_column_option("Y label:", self.__y_log_scale)

        self.__grid_switch = toga.Switch(text="Grid")
        switches = [self.__grid_switch]
        self.__has_legend = has_legend
        if has_legend:
            self.__legend_switch = toga.Switch(text="Legend")
            switches.append(self.__legend_switch)
        else:
            self.__legend_switch = None
        self.add(LineBox(children=switches))

        self.__x_domain_switch = toga.Switch(
            text="Custom X domain", on_change=lambda _: self.x_domain_switch_handler()
        )
        self.__x_min_title = toga.Label("X minimum:", style=Pack(visibility=HIDDEN))
        self.__x_min_input = toga.TextInput(
            style=Pack(visibility=HIDDEN), validators=[Number()]
        )
        self.__x_max_title = toga.Label("X maximum:", style=Pack(visibility=HIDDEN))
        self.__x_max_input = toga.TextInput(
            style=Pack(visibility=HIDDEN), validators=[Number()]
        )
        self.add(
            LineBox(
                children=[
                    self.__x_domain_switch,
                    self.__x_min_title,
                    self.__x_min_input,
                    self.__x_max_title,
                    self.__x_max_input,
                ]
            )
        )

    @property
    def title(self):
        """Getter of the fitting graph title."""
        if self.__title_input.value != "":
            return self.__title_input.value
        if self.__base_name is not None:
            return f"{self.__base_name} - {self.suffix.title()}"
        return self.suffix

    @property
    def file_name(self):
        """Getter of the fitting graph title."""
        if self.__base_name is not None:
            name = (
                f"{self.__base_name.replace(' ', '_')}"
                f"_{self.suffix.replace(' ', '_')}.png"
            )
        else:
            name = f"{self.suffix.replace(' ', '_')}.png"
        return name.lower()

    @property
    def xlabel(self):
        """Getter of the label of the x axis."""
        if self.__xlabel_input.value != "":
            return self.__xlabel_input.value
        if self.__xcolumn is not None:
            return self.__xcolumn
        return None

    @property
    def ylabel(self):
        """Getter of the label of the y axis."""
        if self.__ylabel_input.value != "":
            return self.__ylabel_input.value
        if self.__ycolumn is not None:
            return self.__ycolumn
        return None

    @property
    def grid(self):
        """Should or should not add grid lines to plots."""
        return self.__grid_switch.value

    @property
    def legend(self):
        """Should or should not add legend to plots."""
        return self.__legend_switch is not None and self.__legend_switch.value

    @property
    def x_log_scale(self):
        """Is x axis log scale on or off."""
        return self.__x_log_scale.value

    @property
    def y_log_scale(self):
        """Is y axis log scale on or off."""
        return self.__y_log_scale.value

    @property
    def xmin(self):
        """Get minimum value of X, if presented by user."""
        if not self.__x_domain_switch.value or self.__x_min_input.value == "":
            return None
        try:
            return float(self.__x_min_input.value)
        except ValueError as error:
            raise EddingtonException(
                "X minimum value must a floating number"
            ) from error

    @property
    def xmax(self):
        """Get minimum value of X, if presented by user."""
        if not self.__x_domain_switch.value or self.__x_max_input.value == "":
            return None
        try:
            return float(self.__x_max_input.value)
        except ValueError as error:
            raise EddingtonException(
                "X maximum value must a floating number"
            ) from error

    @property
    def interval(self):
        """Get data interval from the user."""
        return Interval(min_val=self.xmin, max_val=self.xmax)

    def get_plot_kwargs(self):
        """Get plot kwargs from configuration box."""
        kwargs = dict(
            title_name=self.title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            grid=self.grid,
            x_log_scale=self.x_log_scale,
            y_log_scale=self.y_log_scale,
            xmin=self.xmin,
            xmax=self.xmax,
        )
        if self.__has_legend:
            kwargs["legend"] = self.legend
        return kwargs

    def set_scale(self, figure):
        """Set ticks of figure if in log scale."""
        axes = figure.get_axes()[0]
        if self.x_log_scale:
            axes.xaxis.set_major_formatter(EDDINGTON_FORMATTER)
            axes.xaxis.set_minor_locator(NULL_LOCATOR)
        if self.y_log_scale:
            axes.yaxis.set_major_formatter(EDDINGTON_FORMATTER)
            axes.yaxis.set_minor_locator(NULL_LOCATOR)
        return figure

    def on_fitting_function_load(self, fitting_function):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        self.__base_name = (
            None if fitting_function is None else fitting_function.title_name
        )

    def on_fitting_data_load(self, fitting_data):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fitting_data is None:
            self.__xcolumn, self.__ycolumn = None, None
        else:
            self.__xcolumn, self.__ycolumn = (
                fitting_data.x_column,
                fitting_data.y_column,
            )

    def x_domain_switch_handler(self):
        """Handler to run whenever the custom x domain toggle is switched."""
        if self.__x_domain_switch.value:
            self.__x_min_title.style.visibility = VISIBLE
            self.__x_min_input.style.visibility = VISIBLE
            self.__x_max_title.style.visibility = VISIBLE
            self.__x_max_input.style.visibility = VISIBLE
        else:
            self.__x_min_input.value, self.__x_max_input.value = "", ""
            self.__x_min_title.style.visibility = HIDDEN
            self.__x_min_input.style.visibility = HIDDEN
            self.__x_max_title.style.visibility = HIDDEN
            self.__x_max_input.style.visibility = HIDDEN

    def toggle_grid_switch(self, widget):  # pylint: disable=unused-argument
        """Set/unset the grid switch."""
        self.__grid_switch.toggle()

    def toggle_legend_switch(self, widget):  # pylint: disable=unused-argument
        """Set/unset the grid switch."""
        self.__legend_switch.toggle()

    def toggle_x_log_scale(self, widget):  # pylint: disable=unused-argument
        """Set/unset the x log scale switch."""
        self.__x_log_scale.toggle()

    def toggle_y_log_scale(self, widget):  # pylint: disable=unused-argument
        """Set/unset the y log scale switch."""
        self.__y_log_scale.toggle()

    def build_figure_builder(self):
        """Build FigureBuilder to use when drawing."""
        figure_builder = FigureBuilder()
        if self.title is not None:
            figure_builder.add_title(self.title)
        if self.xlabel is not None:
            figure_builder.add_xlabel(self.xlabel)
        if self.ylabel is not None:
            figure_builder.add_ylabel(self.ylabel)
        if self.grid:
            figure_builder.add_grid()
        if self.legend:
            figure_builder.add_legend()
        self.additional_instructions(figure_builder, self.interval)
        return figure_builder

    def on_draw(
        self, chart, figure, *args, **kwargs
    ):  # pylint: disable=unused-argument
        """Draw on figure using the figure builder."""
        if not isinstance(figure, Figure):
            figure = Figure(figure)
        figure_builder = self.build_figure_builder()
        figure_builder.build(figure)
        self.set_scale(figure)

    def __add_column_option(self, label, *additional_widgets):
        text_input = toga.TextInput(style=Pack(width=LONG_INPUT_WIDTH))
        line = LineBox(
            children=[
                toga.Label(text=label, style=Pack(width=LABEL_WIDTH)),
                text_input,
                *additional_widgets,
            ],
        )

        self.add(line)
        return text_input
