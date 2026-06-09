# OperationType Index

## Android

| Operation Type | Description | Documentation |
|---------|------|------|
| `android.device.info` | Get various information about Android devices, including manufacturer, model, platform version, API level, device name, ANDROID_ID, etc. | [android\android.device.info.md] |
| `android.touch.tap` | Performs the Android tap gesture, supporting coordinates, element objects, locators, or element names defined in elements.json. | [android\android.touch.tap.md] |
| `android.element.get` | Find an Android UI element based on a locator or definition in elements.json | [android\android.element.get.md] |
| `android.element.getAll` | Find all matching Android UI elements based on the locator and return a list of elements | [android\android.element.getAll.md] |
| `android.element.getAttribute` | Read the text, contentDesc, bounds and other attributes of Android UI elements | [android\android.element.getAttribute.md] |
| `android.element.input` | Input text to Android UI elements, supporting element objects, locators, focused input boxes, or focusing by coordinates first and then inputting. | [android\android.element.input.md] |
| `android.touch.swipe` | Perform a swipe gesture on the Android screen or a specified element area | [android\android.touch.swipe.md] |
| `android.toast` | Display Android Toast prompt message | [android\android.toast.md] |
| `android.press.back` | Simulate Android return key operation | [android\android.press.back.md] |
| `android.press.home` | Simulate Android home button operation | [android\android.press.home.md] |
| `android.screenshot.capture` | Capture a screenshot and save it to a file | [android\android.screenshot.capture.md] |
| `android.ui.capture` | Capture the UI tree and screenshot simultaneously to ensure an exact match | [android\android.ui.capture.md] |
| `android.ui.dumpTree` | Export the UI tree obtained by the accessibility service as an XML/JSON file | [android\android.ui.dumpTree.md] |
| `android.app.current` | Get the package name of the current foreground Android application, used to determine which application it is currently in | [android\android.app.current.md] |
| `android.app.launch` | Launch the specified Android application through the package name | [android\android.app.launch.md] |

## Browser

| Operation Type | Description | Documentation |
|---------|------|------|
| `browser.close` | Closes the Playwright browser instance and releases resources | [browser\browser.close.md] |
| `browser.element.click` | Click on the specified page element | [browser\browser.element.click.md] |
| `browser.element.get` | Get a single element via CSS selector | [browser\browser.element.get.md] |
| `browser.element.getAll` | Get all matching elements via CSS selector | [browser\browser.element.getAll.md] |
| `browser.element.getAttribute` | Get the attribute value of an element | [browser\browser.element.getAttribute.md] |
| `browser.element.getText` | Get the text content of the element | [browser\browser.element.getText.md] |
| `browser.element.hover` | Hover the mouse over the specified element | [browser\browser.element.hover.md] |
| `browser.element.input` | Enter text into the specified element | [browser\browser.element.input.md] |
| `browser.element.select` | Select an option in a drop-down list | [browser\browser.element.select.md] |
| `browser.navigate.back` | Go back to the previous page | [browser\browser.navigate.back.md] |
| `browser.navigate.forward` | Forward to the next page | [browser\browser.navigate.forward.md] |
| `browser.navigate.refresh` | Refresh the current page | [browser\browser.navigate.refresh.md] |
| `browser.navigate.to` | Navigates to the specified URL | [browser\browser.navigate.to.md] |
| `browser.open` | Launch a Playwright browser instance, supporting headless mode and custom viewports | [browser\browser.open.md] |
| `browser.ref.resolve` | Converts a ref reference into a precise CSS selector, used to obtain the specific positioning information of the element | [browser\browser.ref.resolve.md] |
| `browser.screenshot.capture` | Take a screenshot of the current page | [browser\browser.screenshot.capture.md] |
| `browser.screenshot.element` | Take a screenshot of the specified element | [browser\browser.screenshot.element.md] |
| `browser.script.evaluate` | Execute a JavaScript expression and save the result to a variable | [browser\browser.script.evaluate.md] |
| `browser.script.execute` | Execute JavaScript code in the page | [browser\browser.script.execute.md] |
| `browser.snapshot` | Get the ARIA tree of the current page and generate element reference mapping | [browser\browser.snapshot.md] |
| `browser.tab.close` | Close the tab of the specified index (if not specified, close the current tab) | [browser\browser.tab.close.md] |
| `browser.tab.open` | Open a new browser tab | [browser\browser.tab.open.md] |
| `browser.tab.switch` | Switch to the tab page at the specified index | [browser\browser.tab.switch.md] |
| `browser.wait.forElement` | Wait for the element to reach the specified state (attached, detached, visible, hidden) | [browser\browser.wait.forElement.md] |
| `browser.wait.forNavigation` | Wait for page navigation to complete | [browser\browser.wait.forNavigation.md] |

## Core

| Operation Type | Description | Documentation |
|---------|------|------|
| `application.execute` | Execute the main process (__main__.json) of other applications, supporting parameter passing, version selection and return value collection | [core\application.execute.md] |
| `break` | Break executor - break out of the current loop or a loop at the specified level | [core\break.md] |
| `console.write` | Cross-platform console output log information, using the unified log system to support color output and variable replacement | [core\console.write.md] |
| `container` | A container that performs multiple operations sequentially | [core\container.md] |
| `continue` | Continue executor - skip the current iteration of the current loop and continue with the next iteration | [core\continue.md] |
| `custom.java` | Execute user-defined Java static methods. Supports parameter passing and return values. Users can create Java files in the application's custom directory and write static methods containing Map<String, Object> parameters. | [core\custom.java.md] |
| `for` | For loop executor that supports multiple loop modes such as numeric range loop, array traversal, string traverse, etc. | [core\for.md] |
| `ifelse` | Execute different branch operations based on conditional expressions | [core\ifelse.md] |
| `json.format` | Convert compressed JSON string to indented prettified format | [core\json.format.md] |
| `jsonata.transform` | Query, filter and transform JSON data using JSONata expressions | [core\jsonata.transform.md] |
| `log.write` | Export the collected console.write logs to a file, supporting level filtering, append mode and variable replacement | [core\log.write.md] |
| `raiseerror` | Actively raise error executor - for customizing error conditions and error messages | [core\raiseerror.md] |
| `return` | Terminate template execution early and return | [core\return.md] |
| `template.execute` | Call the subtemplate and execute it, support parameter passing and OUTPUT collection, configurable timeout and failure handling strategies | [core\template.execute.md] |
| `trycatch` | Try-Catch-Finally executor - provides structured error handling | [core\trycatch.md] |
| `variable.assign` | Variable assignment executor - supports simple assignments and arithmetic expressions | [core\variable.assign.md] |
| `wait.duration` | Fixed duration wait, supports millisecond precision | [core\wait.duration.md] |
| `wait.for` | Polling waits for conditions to be met, supports timeout and polling interval configuration, and can poll up to 10,000 times | [core\wait.for.md] |
| `while` | Loop executor that supports precondition loop (while) and postcondition loop (do-while) | [core\while.md] |

## Database

| Operation Type | Description | Documentation |
|---------|------|------|
| `database.connect` | Create a SQL Server database connection, support connection string or parameter configuration | [database\database.connect.md] |
| `database.execute` | Execute SQL Server query or update statement, support parameterized query and result set output | [database\database.execute.md] |

## Dataprocessing

| Operation Type | Description | Documentation |
|---------|------|------|
| `datetime.process` | Date and time processing operations - supports parsing, formatting, calculation, comparison, obtaining time components, etc. | [dataprocessing\datetime.process.md] |
| `dict.process` | Dictionary processing operations - supports getting, setting, deleting, traversing, merging, etc. | [dataprocessing\dict.process.md] |
| `json.parse` | JSON parsing operation - supports parsing, generation, path query, formatting, etc. | [dataprocessing\json.parse.md] |
| `list.process` | List processing operations - supports adding, deleting, sorting, filtering, etc. | [dataprocessing\list.process.md] |
| `regex` | Regular expression operations - supports matching, search, replacement, extraction, etc. | [dataprocessing\regex.md] |
| `string.process` | String processing operations - supports splitting, replacing, intercepting, case conversion, etc. | [dataprocessing\string.process.md] |
| `type.convert` | Data type conversion operation - supports string, number, Boolean and other type conversions | [dataprocessing\type.convert.md] |

## File

| Operation Type | Description | Documentation |
|---------|------|------|
| `file.append` | Append content to the end of the file | [file\file.append.md] |
| `file.delete` | Delete the specified file | [file\file.delete.md] |
| `file.exists` | Checks if a file exists and returns a boolean value | [file\file.exists.md] |
| `file.read` | Read the file content and store it in a variable | [file\file.read.md] |
| `file.write` | Write content to a file (overwrite mode) | [file\file.write.md] |

## Network

| Operation Type | Description | Documentation |
|---------|------|------|
| `http.get` | Send HTTP GET request to obtain data, support query parameters | [network\http.get.md] |
| `http.post` | Send HTTP POST request to submit data, supporting JSON, form and other content types | [network\http.post.md] |
| `http.upload` | Upload files to the server, supports local files, Base64 data and URL query parameters | [network\http.upload.md] |
| `mail.smtp` | Send email via SMTP protocol, support SSL/TLS encryption and attachment function | [network\mail.smtp.md] |

## Testing

| Operation Type | Description | Documentation |
|---------|------|------|
| `assert.contains` | Assert that the string contains the specified substring. If it does not contain the specified substring, the execution will fail | [testing\assert.contains.md] |
| `assert.equals` | Asserts that two values ​​are equal, failing if they are not equal | [testing\assert.equals.md] |
| `assert.true` | Assert that a conditional expression is true, supporting complex logical expressions and variable substitution | [testing\assert.true.md] |

## Windows

| Operation Type | Description | Documentation |
|---------|------|------|
| `win.device.info` | Obtain various information about Windows computers, including manufacturer, computer name, user name, operating system version, architecture, etc. | [windows\win.device.info.md] |
| `win.element.click` | Click on a Windows UI element (via XPath or elements.json) | [windows\win.element.click.md] |
| `win.element.get` | Find Windows UI elements based on definitions in elements.json | [windows\win.element.get.md] |
