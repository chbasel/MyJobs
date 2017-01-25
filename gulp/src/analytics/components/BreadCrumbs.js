import React from 'react';
import {Component} from 'react';

class BreadCrumbs extends Component {
  render() {
    const {crumbs} = this.props;
    const breadcrumbs = crumbs.map((breadcrumb, i) => {
      return (
        <li key={i} className="analytics-breadcrumbs">
          <a className="breadcrumb-active" href="#">{breadcrumb.name}</a>
        </li>
      );
    });
    return (
      <ul className="breadcrumbs-container">
        {breadcrumbs}
      </ul>
    );
  }
}

BreadCrumbs.propTypes = {
  crumbs: React.PropTypes.arrayOf(React.PropTypes.object),
};

export default BreadCrumbs;
