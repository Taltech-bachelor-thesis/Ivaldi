
# Components

This directory holds application 'components'. These are parts of the application that do not have their own
window. Things such as `CustomCanvas` or `toolbar` because they do not have their own window and are both rendered
inside MainDiagram
---

## CustomCanvas

`CustomCanvas` is a wrapper for `tkinter.Canvas` that all `canvas_objects` are drawn on.

### CustomCanvas parameters

| **Parameter**         | **Type**     | **Description**                                                                                                                                                                 | 
|-----------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| master                | Tk           | The parent widget of this canvas. If None, tkinter will attempt to use the default root.                                                                                        |
| main_diagram          | MainDiagram  | MainDiagram object used for accessing variables across the application.                                                                                                         |
|                       |              |                                                                                                                                                                                 |
| # **Optional params** |              |                                                                                                                                                                                 |
| id_                   | int          | Custom ID for canvas.                                                                                                                                                           |
| is_search             | boolean      | States whether the CustomCanvas object is created for the search window and is not part of the regular diagram.<br/> Default value is `False`. This disables some features.     |
| diagram_source_box    | Box          | Source Box for sub-diagram. A Box object that the currently CustomCanvas is located in. This is only used if the a CustomCanvas is a sub-diagram.<br/> Default value is `None`. |
| **kwargs              |              | Kwargs for `tkinter.Canvas`                                                                                                                                                     |


### CustomCanvas variables

| **Variable**             | **Type**               | **Descriptions**                                                                                                                                                    |
|--------------------------|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| selector                 | Selector               | The Selector object used for dealing with Selected objects.                                                                                                         |
| parent_diagram           | CustomCanvas           | The parent diagram of the CustomCanvas.                                                                                                                             |
| main_diagram             | MainDiagram            | The MainDiagram object.                                                                                                                                             |
| master                   | Tk                     | The parent widget of this canvas.                                                                                                                                   |
| is_search                | boolean                | Specifies whether the canvas is created for the searching window.                                                                                                   |
| boxes                    | list                   | List of Boxes. Contains every Box objects that exists on the Canvas at the moment.                                                                                  |
| outputs                  | list                   | List of Connections. Contains the outputs of the diagram (the Connections on the right side).                                                                       |
| inputs                   | list                   | List of Connections. Contains the inputs of the diagram (the Connections on the left side).                                                                         |
| spiders                  | list                   | List of Spiders. Contains all Spider objects present in the CustomCanvas.                                                                                           |
| wires                    | list                   | List of Wires. Contains all Wire objects present in the CustomCanvas.                                                                                               |
| corners                  | list                   | List of Corners. Contains all Corner objects that are on the CustomCanvas.                                                                                          |
| temp_wire                | Wire                   | Temporary Wire variable. Used when pulling/creating wires, the temporary wire is the Wire that is seen during Wire pulling.                                         |
| temp_end_connection      | Connection             | Temporary end connection Variable. During Wire pulling an end Connection is required to create a temporary Wire. This is the variable for the temporary Connection. |
| pulling_wire             | boolean                | Boolean stating whether or not wire pulling is currently active.                                                                                                    |
| quick_pull               | boolean                | Boolean stating whether quick pull (wire pulling from double clicking a Connection) is active.                                                                      |
| receiver                 | Receiver               | The Receiver object that is used to send information to the backend.                                                                                                |
| current_wire_start       | Connection             | Connection that is used to remember where the Wire creation was started from.                                                                                       |
| draw_wire_mode           | boolean                | Boolean stating whether the CustomCanvas is in draw wire mode.                                                                                                      |
| diagram_source_box       | Box                    | Box that holds the CustomCanvas object, used when CustomCanvas is a sub-diagram.                                                                                    |
| name_text                | string                 | String of CustomCanvas name.                                                                                                                                        |
| select_box               | int                    | The rectangle that is created when selecting items.                                                                                                                 |
| selecting                | boolean                | Boolean stating if selecting is active.                                                                                                                             |
| copier                   | Copier                 | Copier object.                                                                                                                                                      |
| hypergraph_exporter      | HypergraphExporter     | HypergraphExporter object.                                                                                                                                          |
| context_menu             | tkinter.Menu           | Tkinter Menu object used for creating context menus on the CustomCanvas.                                                                                            |
| tree_logo                | PIL.ImageTk.PhotoImage | Logo that is used for the button that opens the treeview.                                                                                                           |
| search_result_button     | SearchResultButton     | SearchResultButton object.                                                                                                                                          |
| box_shape                | string                 | Default shape of a Box created in CustomCanvas.                                                                                                                     |
| copy_logo                | PIL.ImageTk.PhotoImage | Logo that is used for in the copy button of TikZ interface.                                                                                                         |
| total_scale              | float                  | The current scale of the CustomCanvas. Minimum scale is `1.0`.                                                                                                      |
| delta                    | float                  | The amount that will be zoomed in or out. Default is `0.75`.                                                                                                        |
| prev_width_max           | int                    | Previous maximum width of the CustomCanvas. Updated on CustomCanvas size change.                                                                                    |
| prev_height_max          | int                    | Previous maximum height of the CustomCanvas. Updated on CustomCanvas size change.                                                                                   |
| prev_width_min           | int                    | Previous minimum width of the CustomCanvas. Updated on CustomCanvas size change.                                                                                    |
| prev_height_min          | int                    | Previous minimum height of the CustomCanvas. Updated on CustomCanvas size change.                                                                                   |
| prev_scale               | float                  | Previous zoom scale of CustomCanvas.                                                                                                                                |
| pan_speed                | int                    | Speed of panning.                                                                                                                                                   |
| hover_item               | Any                    | Item that is currently being hovered over. This may not show all items being hovered on.                                                                            |
| search_result_highlights | list                   | List containing highlighted objects when showing search results.                                                                                                    |
| wire_label_tags          | list                   | List of tags that represent the Wire labels on the CustomCanvas.                                                                                                    |


### CustomCanvas functions

    .on_hover(item)
        Activated when some items are being hovered over. Updates the hover_item variable.

        Parameters:
            item (Any): A canvas_object widget to change hover_item to.

    .on_leave_hover()
        Changes hover_item to `None`. Activated when leaving hover over objects.

    .scale_item(event)
        Activates `.on_resize_scroll(event)` on the item that is being hovered over.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .toggle_search_results_button()
        Toggles visibility of search result button based on active search status. Search result button is the button
        used for moving between search results and cancelling search results.

    .update_search_result_button()
        Updates the search result button, moving it to the correct location.

    .remove_search_highlights()
        Removes search highlights from CustomCanvas. Toggles search results button.

    .select_all()
        Selects all the objects on the CustomCanvas.

    .update_prev_winfo_size()
        Updates previous height/width variables with current CustomCanvas size.

    .pan_horizontal(event)
        Moves objects on the CustomCanvas horizontally.
        
        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .pan_vertical(event)
        Moves objects on the CustomCanvas vertically.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .move_boxes_spider(attr, multiplier)
        Moves boxes and spiders on the CustomCanvas along the x or y-axis. 

        Parameters:
            attr (string): `x` or `y`. Axis to move objects along.
            multiplier (int): -1 or 1. Determines whether objects will be moved towards negative coordinates or positive coordinates.

    .delete(*args)
        Tkinter.Canvas delete function with added hypergraph changes.

        *args: Tkinter.Canvas .delete(*args)

    .handle_right_click(event)
        Handles right click event on CustomCanvas. Possible actions are finishing selection, cancelling wire pulling,
        showing context menu.

        Parameters:
            event (tkinter.Event): Event object passed on key press.

    .set_name(name)
        Set new name for CustomCanvas.

        Parameters:
            name (string): New name for CustomCanvas.

    .reset_zoom()
        Resets the scale of the CustomCanvas to be zoomed out all the way.

    .zoom(event)
        Zooming main function, actived on scrolling on CustomCanvas. Scales the canvas.

        Parameters:
            event (tkinter.Event): Event object passed on key press.

    .update_coordinates(denominator, event, scale)
        Moves all (corners, i/o, boxes, spiders) objects according to zooming.

        Parameters:
            denominator (float): delta or 1/delta used for calculating zoom distances.
            event (tkinter.Event): Event object passed from key press.
            scale (float): The amount of scale change from zoom.

    .check_max_zoom(x, y, denominator)
        Checks whether zooming out from the specified location is allowed.
        Returns a tuple containing a boolean if the zoom is allowed, how much x needs to be offset to zoom out normally,
        how much y needs to be offset to zoom out normally, and boolean stating if corners are at CustomCanvas corners.

        Parameters:
            x (int): x coordinate where zooming out is done.
            y (int): y coordinate where zooming out is done.
            denominator (float): delta or 1/delta used for calculating zoom distances.

    .check_corner_start_locations()
        Checks if all Corner objects are in CustomCanvas corners. Returns boolean.

    .close_menu()
        Closes CustomCanvas context menu.

    .show_context_menu(event)
        Creates and displaying context menu for CustomCanvas.

        Parameters:
            event (tkinter.Event): Event object passed from key press, holds location for menu.
            
    .is_mouse_on_object(event)
        Returns boolean stating if the mouse is on an object.
    
        Parameters:
            event (tkinter.Event): Event object passed from key press. Location that will be checked.

    .__select_start__(event)
        Start a selection box from event location.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .__select_motion__(event)
        Updates selection area.
        
        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .__select_release__()
        Ends the active selection.

    .pull_wire(event)
        Start quick pulling wire from event, if event is overlapping with a Connection.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .get_connection_from_location(event)
        Returns Connection or None that is at event location.

        Parameters:
            event (tkinter.Event): Event object passed from keybind.

    .on_canvas_click(event, connection)
        Handles click on canvas. Checks if click was on Connection, if so then activates connection click handling.
        Otherwise finishes selection.

        Parameters:
            event (tkinter.Event): Event object passed from key press.
            connection (Connection): (Optional) Connection that was clicked on. Will handle click on Connection directly.

    .start_pulling_wire(event)
        Starts creating a temporary Wire to the mouse location from a chosen start connection, during draw wire mode.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .handle_connection_click(c, event)
        Handles click on Connection object, redirects to other functions based on application state.
        
        Parameters:
            c (Connection): Connection object that was clicked.
            event (tkinter.Event): Event object sent from key press.

    .start_wire_from_connection(connection, event)
        Sets current_wire_start variable to given Connection object. If event is given, draws a temporary Connection on
        event location.

        Parameters:
            connection (Connection): Connection object that wire is started from.
            event (tkinter.Event): (Optional) Event object passed from key press.

    .end_wire_to_connection(connection, bypass_legality_check)
        Deletes temporary Wire and Connection to create a non-temporary Wire from current_wire_start to given connection
        in params. If given connection is same as current_wire_start then wire pulling is cancelled and no Wire is created.
        Before creating a non-temporary Wire legality checking is done, if this does not pass a Wire is not created.

        Parameters:
            connection (Connection): End Connection of where Wire would be created.
            bypass_legality_check (boolean): (Optional) Boolean to bypass legality checking on Wire creation.

    .cancel_wire_pulling(event)
        Cancels creating a Wire and resets all variables used for it.

        Parameters:
            event (tkinter.Event): (Optional) Event object passed from key press.

    .nullify_wire_start()
        Changes current_wire_start color back to 'black' and resets the variable to None.

    .add_box(loc, size, id_, style)
        Creates a Box object. Location, size, id and shape of the Box can be specified with additional params.
        Returns the created Box tag.

        Parameters:
            loc (tuple): (Optional) Location that the Box will be created at. Default is (100, 100)
            size (tuple): (Optional) Size of the Box that will be created. Default is (60, 60)
            id_ (int): (Optional) Custom set ID for the Box that will be created.
            style (string): (Optional) Specify style of the Box that will be created. Default is the canvas selected style.

    .get_box_by_id(box_id)
        Returns Box object with given id. Returns None if no Box with given id found.

        Parameters:
            box_id (int): ID of Box that is searched for.

    .get_box_function(box_id)
        Returns the BoxFunction object of a Box with given id.

        Parameters:
            box_id (int): ID of Box that BoxFunction will be returned for.

    .add_spider(loc, id, connection_type)
        Creates a Spider object. Location, id and connection_type can be specified with additional parameters.
        Returns the created Spider tag.

        Parameters:
            loc (tuple): (Optional) Location that the Spider will be created on. Default is (100, 100).
            id_ (int): (Optional) ID that will be added to the created Spider.
            connection_type (ConnectionType): (Optional) Defines the type of the Spider that will be created. Default value is ConnectionType.GENERIC.

    .add_spider_with_wires(start, end, x, y)
        Creates a Spider at (x, y) location and connects the newly created Spider to start and end Connections given in params.

        Parameters:
            start (Connection): Connection that created Spider will have a Wire connected to.
            end (Connection): Connection that created Spider will have a Wire connected to.
            x (int): X coordinate that Spider is created on.
            y (int): Y coordinate that Spider is created on.

    .save_as_png()
        Resets the zoom of the CustomCanvas and asks the user where they would like to save the png file. Afterwards
        creates png in MainDiagram.

    .open_tikz_generator()
        Resets the zoom of the CustomCanvas and opens a small window that will have the generated TikZ code.

    .toggle_draw_wire_mode()
        Toggles draw wire mode on CustomCanvas.

    .on_canvas_resize(_)
        Updates the locations on Corner objects and diagram inputs and outputs along with previous winfo sizes and canvas
        label location. This is activated when the application is configured.

        Parameters:
            _ (tkinter.Event): Event object that is passed from application configuration.

    .__on_configure_move__()
        Moves Spiders and Boxes to their relative current positions.
        
        This function is used when the canvas is configured, it will keep items in their relative positions, movement is
        done with bypassing legality.

    .debounce(wait_time)
        Decorator that will debounce a function so that it is called after wait_time seconds.
        If it is called multiple times, will wait for the last call to be debounced and run only this one.
        
        Parameters:
            wait_time (int): Seconds that debouncer will wait for before activating a function.

    .init_corners()
        Sets Corner objects to CustomCanvas corners and updates diagram inputs/outputs.

    .update_corners()
        Updates Corner objects to be at correct locations when application configuration is done when not being zoomed out.

    .update_inputs_outputs()
        Updates the locations of diagram inputs and outputs.

    .delete_everything()
        Deletes everything on the CustomCanvas.

    .is_wire_between_connections_legal(start, end)
        Checks if a wire that is created between start and end Connections is legal.

        Parameters: 
            start (Connection): Would be start Connection of the Wire. 
            end (Connection): Would be end Connection fo the Wire.

    .random()
        Creates Wires between Connections at random.

    .add_diagram_output(id_, connection_type)
        Adds an output to the diagram. ID and type of Connection can be specified with additional parameters.
        Returns created Connection tag.

        Parameters:
            id_ (int): ID that will be added to the created output Connection.
            connection_type (ConnectionType): Type that the output Connection will be. Default is ConnectionType.GENERIC.

    .add_diagram_input_for_sub_d_wire(id_)
        If the CustomCanvas is a sub-diagram then this will add a left Connection to the source box of the diagram as
        well as to the diagram itself. Returns a tuple of source box Connection tag and diagram Connection tag.
        
        Parameters:
            id_ (int): (Optional) ID that will be given to the input created on the diagram.

    .add_diagram_output_for_sub_d_wire(id_)
        If the CustomCanvas is a sub-diagram then this will add a right Connection to the source box of the diagram as
        well as to the diagram itself. Returns a tuple of source box Connection tag and diagram Connection tag.

        Parameters:
            id_ (int): (Optional) ID that will be given to the output created on the diagram.

    .remove_diagram_output()
        Removes an output Connection from diagram outputs.

    .add_diagram_input(id_, connection_type)
        Adds an input to the diagram. ID and type of Connection can be specified with additional parameters.
        Returns created Connection tag.

        Parameters:
            id_ (int): ID that will be added to the created input Connection.
            connection_type (ConnectionType): Type that the input Connection will be. Default is ConnectionType.GENERIC.

    .remove_diagram_input()
        Removes an input Connection from diagram inputs.

    .remove_specific_diagram_input(con)
        Remove a specified Connection from diagram inputs.
        
        Parameters:
            con (Connection): Diagram input Connection that will be removed.

    .remove_specific_diagram_output(con)
        Remove a specified Connection from diagram outputs.

        Parameters:
            con (Connection): Diagram output Connection that will be removed.

    .export_hypergraph()
        Resets zoom and exports hypergraph.

    .calculate_zoom_dif(zoom_coord, object_coord, denominator)
        Returns the amount that an object is moved when zooming. Result is rounded to 4 places.

        Parameters:
            zoom_coord (int): Location where zooming is done. This is a singular coordinate, not both x and y.
            object_coord (int): Location of the object during zooming. This is a singular coordinate, not both x and y.
            denominator (float): Used for calculating how much object will move.

    .set_box_shape(shape)
        Changes box_shape variable to shape parameter.
    
        Parameters:
            shape (string): New default shape for Boxes.

    .paste_copied_items(event)
        Pastes copied items at event location. Will replace previously selected items if they exist.
    
        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .cut_selected_items()
        Copies selected items and then deletes them.

    .create_sub_diagram()
        Creates a sub-diagram with selected items.

    .find_paste_multipliers()
        Find multipliers for pasting with replace. This is used to make the pasted part smaller so it would fit in the 
        replaced parts location.
        Returns multiplier and x, y coordinate where paste would be placed.

        Parameters:
            x (int): x coordinate of the middle of the replacing area.
            y (int): y coordinate of the middle of the replacing area.
            x_length (int): width of the copied area.
            y_length (int): height of the copied area.





## SearchResultButton

SearchResultButton is a button that is shown after a search has been conducted on the CustomCanvas. 

The buttons purpose is to display information about the search and allow moving between results.

It shows the number of results as well as the currently primarily highlighted parts index.

It has 2 buttons that allow moving between results.

It has a button to turn off search results. It will turn off search highlights and toggle off the button.

### SearchResultButton parameters

| **Params**   | **Type**    | **Description**                                      |
|--------------|-------------|------------------------------------------------------|
| master       | Tk          | Master Tk object that the button will be created on. |
| main_diagram | MainDiagram | MainDiagram object to access functions.              |
| **kwargs     |             | Keyword arguments for LabelFrame.                    |

### SearchResultButton variables

| **Variable**       | **Type**           | **Description**                                                   |
|--------------------|--------------------|-------------------------------------------------------------------|
| main_diagram       | MainDiagram        | MainDiagram object used for accessing functions.                  |
| close_button_frame | tkinter.LabelFrame | LabelFrame that holds the close button.                           |
| close_icon         | ImageTk.PhotoImage | Close icon that is displayed on close button.                     |
| up_icon            | ImageTk.PhotoImage | Up icon that is displayed on the up button.                       |
| down_icon          | ImageTk.PhotoImage | Down icon that is displayed on the down button.                   |
| info_frame         | tkinter.LabelFrame | LabelFrame that holds information text.                           |
| info_text          | tkinter.StringVar  | Holds string that is displayed in information part of the button. |
| info_label         | tkinter.Label      | Label that holds info_text and is displayed on info_frame.        |

---

## Toolbar

Toolbar is the file menu bar of our application. It holds different save, generation, importing functions along with settings.

```
Toolbar
|
└--- File
|    └--- Save as
|    |    └--- png file
|    |    └--- project
|    |    └--- hypergraph
|    |
|    └--- Generate
|    |    └--- TikZ
|    |    └--- code
|    |
|    └--- New
|    └--- Import new diagram
|    └--- Import as sub-diagram
|
└--- Edit
|    └--- Search in Project
|
└--- View
     └--- Visualize hypergraph

```

### Toolbar parameters

| **Param**    | **Type**    | **Description**                                             | 
|--------------|-------------|-------------------------------------------------------------|
| main_diagram | MainDiagram | MainDiagram used to access functions offered in the toolbar |

### Toolbar variables

| **Variable**      | **Type**           | **Description**                                                                   |
|-------------------|--------------------|-----------------------------------------------------------------------------------|
| main_diagram      | MainDiagram        | MainDiagram object used to access functions.                                      |
| file_button       | tkinter.Menubutton | Menubutton that holds File menu.                                                  |
| file_menu         | tkinter.Menu       | Menu that is opened when pressing file_button. Holds File sub-menus and commands. |
| save_submenu      | tkinter.Menu       | Save sub-menu. Holds commands about saving.                                       |
| generate_submenu  | tkinter.Menu       | Generation sub-menu. Holds commands about generation.                             |
| edit_button       | tkinter.Menubutton | Menubutton that holds Edit menu.                                                  |
| edit_menu         | tkinter.Menu       | Menu that is opened when pressing edit_button.                                    |
| view_button       | tkinter.Menubutton | Menubutton that holds View menu.                                                  |
| view_menu         | tkinter.Menu       | Menu for View commands.                                                           |
| help_logo         | ImageTk.PhotoImage | Help logo that is used to open the help window.                                   |
| canvas_name_text  | tkinter.StringVar  | StringVar that holds the text for the canvas name.                                |
| canvas_name_label | ttkbootstrap.Label | Label that holds the canvas name and is shown in the Toolbar.                     |

### Toolbar functions.

    .open_help_window()
        Creates HelpWindow object. Displaying it in a new window.
    
    .import_sub_diagram()
        Imports a new diagram as a sub-diagram of the currently opened diagram.
    
    .update_canvas_label()
        Update canvas name label in the Toolbar.

    .confirm_deletion()
        Opens a dialog for the user asking for confirmation about unsaved progress deletion.

    .handle_new_graph(import_)
        Handles creating new diagram. Will delete everything except root canvas if root canvas has any objects.
        If specified with parameter then it will also load a new diagram to the new blank canvas.
        
        Parameters:
            import_ (bool): (Optional) Specifies whether a new diagram should be imported after deleting the old diagram. Default is False.

