"""Utility functions for rendering car tables as HTML."""


def get_table_html(cars_df):
    """
    Generates the HTML table from the car listings DataFrame.

    Args:
        cars_df (pd.DataFrame): DataFrame containing car details.

    Returns:
        str: The HTML string for the table.
    """
    # Select relevant columns
    columns = [
        "make",
        "model",
        "price",
        "mileage",
        "year",
        "score",
        "grade",
        "url",
        "img_url",
    ]
    cars_df = cars_df[columns]

    # Convert URL to clickable links
    cars_df["url"] = cars_df["url"].apply(lambda x: f'<a href="{x}">Link</a>')

    # Format the table with embedded images
    table_html = """
    <html>
    <body>
    <h2>Latest Car Listings</h2>
    <table border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th>Make</th>
            <th>Model</th>
            <th>Price</th>
            <th>Mileage</th>
            <th>Year</th>
            <th>Score</th>
            <th>Grade</th>
            <th>Listing</th>
            <th>Image</th>
        </tr>
    """

    for _, row in cars_df.iterrows():
        highlight_style = "background-color: yellow;" if row["score"] > 24 else ""
        table_html += f"""
        <tr style=\"{highlight_style}\">
            <td>{row['make']}</td>
            <td>{row['model']}</td>
            <td>{row['price']}</td>
            <td>{row['mileage']}</td>
            <td>{row['year']}</td>
            <td>{row['score']}</td>
            <td>{row['grade']}</td>
            <td>{row['url']}</td>
            <td><img src=\"{row['img_url']}\" class=\"table-img\" alt=\"car image\"></td>
        </tr>
        """

    table_html += """
    </table>
    </body>
    </html>
    """

    return table_html
