import React from 'react';
import {Component} from 'react';

class TableColumns extends Component {
  render() {
    const {columnData} = this.props;
    const col = columnData.PageLoadData.column_names;
    const colHeaders = col.map((colData) => {
      return (
        <th key={colData.key}>{colData.label}</th>
      );
    });
    return (
      <thead>
        <tr>{colHeaders}</tr>
      </thead>
    );
  }
}

TableColumns.propTypes = {
  columnData: React.PropTypes.object.isRequired,
};

export default TableColumns;
