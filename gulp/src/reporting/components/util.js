import {map, groupBy, indexBy} from 'lodash-compat/collection';


/**
 * Build composite controls out of controls with the same display name.
 *
 *  controls: a list of control specs
 *
 *  i.e. this input:
 *  [
 *    {
 *      filter: "partner",
 *      interface_type: "search_multiselect",
 *      display: "Partners"
 *    },
 *    {
 *      filter: "partner_tags",
 *      interface_type: "tags",
 *      display: "Partners"
 *    },
 *  ]
 * produces:
 *  [
 *    {
 *      interface_type: "composite",
 *      filter: "partner+partner_tags",
 *      display: "Partners",
 *      interfaces: {
 *        search_multiselect: {
 *          filter: "partner",
 *          interface_type: "search_multiselect",
 *          display: "Partners"
 *        },
 *        tags: {
 *          filter: "partner_tags",
 *          interface_type: "tags",
 *          display: "Partners"
 *        },
 *      },
 *    },
 *  ]
 *
 * Blended controls can appear anywhere in the control list and be interspersed
 * with non-blended controls.
 */
export function blendControls(controls) {
  const groups = groupBy(controls, 'display');
  const added = {};
  const source = [...controls];
  const result = [];

  // preserve original order
  while (source.length) {
    const current = source.shift();
    const group = groups[current.display];

    if (group.length === 1) {
      // Pass through a singleton group.
      result.push(group[0]);
    } else {
      // Build a composite control
      if (!added[current.display]) {
        const indexed = indexBy(group, 'interface_type');
        const filter = map(group, c => c.filter).join('+');
        result.push({
          filter,
          interface_type: 'composite',
          display: current.display,
          interfaces: indexed,
        });
        added[current.display] = true;
      }
    }
  }
  return result;
}
