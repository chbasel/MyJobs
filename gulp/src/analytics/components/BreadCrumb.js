import React from 'react';
import {Component} from 'react';

class BreadCrumb extends Component {
  render() {
    const {breadcrumbClick, crumbs} = this.props;
    const breadcrumbs = crumbs.map((crumb, i) => {
      return (
        <li key={i} onClick={() => breadcrumbClick(crumb)} className="analytics-breadcrumbs">
          <a className="crumb-title breadcrumb-active" href="#">{crumb}</a>
        </li>
      );
    });
    return (
      <ul className="breadcrumb-container">
        {breadcrumbs}
      </ul>
    );
  }
}

BreadCrumb.propTypes = {
  crumbs: React.PropTypes.array.isRequired,
  breadcrumbClick: React.PropTypes.func,
};

export default BreadCrumb;
