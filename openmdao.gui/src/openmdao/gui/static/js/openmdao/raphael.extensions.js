// ┌────────────────────────────────────────────────────────────────────┐ \\
// │ Raphaël 2.1.0 - JavaScript Vector Library, extensions for openmdao │ \\
// └────────────────────────────────────────────────────────────────────┘ \\


// ┌────────────────────────────────────────────────────────────────────┐ \\
// │ connection from the example at: http://raphaeljs.com/graffle.js    │ \\
// └────────────────────────────────────────────────────────────────────┘ \\

Raphael.fn.connection = function (obj1, obj2, line, bg) {
    if (obj1.line && obj1.from && obj1.to) {
        line = obj1;
        obj1 = line.from;
        obj2 = line.to;
    }

    var bb1 = obj1.getBBox(),
        bb2 = obj2.getBBox(),
        p = [{x: bb1.x + bb1.width / 2,  y: bb1.y - 1},
             {x: bb1.x + bb1.width / 2,  y: bb1.y + bb1.height + 1},
             {x: bb1.x - 1,              y: bb1.y + bb1.height / 2},
             {x: bb1.x + bb1.width + 1,  y: bb1.y + bb1.height / 2},
             {x: bb2.x + bb2.width / 2,  y: bb2.y - 1},
             {x: bb2.x + bb2.width / 2,  y: bb2.y + bb2.height + 1},
             {x: bb2.x - 1,              y: bb2.y + bb2.height / 2},
             {x: bb2.x + bb2.width + 1,  y: bb2.y + bb2.height / 2}],
        d = {}, dis = [],
        i, j, dx, dy, res;

    for (i = 0; i < 4; i++) {
        for (j = 4; j < 8; j++) {
            dx = Math.abs(p[i].x - p[j].x);
            dy = Math.abs(p[i].y - p[j].y);
            if ((i == j - 4) ||
                (((i !== 3 && j !== 6) || p[i].x < p[j].x) &&
                 ((i !== 2 && j !== 7) || p[i].x > p[j].x) &&
                 ((i !== 0 && j !== 5) || p[i].y > p[j].y) &&
                 ((i !== 1 && j !== 4) || p[i].y < p[j].y))) {
                dis.push(dx + dy);
                d[dis[dis.length - 1]] = [i, j];
            }
        }
    }

    if (dis.length === 0) {
        res = [0, 4];
    }
    else {
        res = d[Math.min.apply(Math, dis)];
    }

    var x1 = p[res[0]].x,
        y1 = p[res[0]].y,
        x4 = p[res[1]].x,
        y4 = p[res[1]].y;

    dx = Math.max(Math.abs(x1 - x4) / 2, 10);
    dy = Math.max(Math.abs(y1 - y4) / 2, 10);

    var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
        y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
        x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
        y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);

    var path = ["M", x1.toFixed(3), y1.toFixed(3),"C", x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3)].join(",");

    if (line && line.line) {
        if (line.bg) {
            line.bg.attr({path: path});
        }
        line.line.attr({path: path});
    }
    else {
        var color = typeof line == "string" ? line : "#000";
        return {
            bg: bg && bg.split && this.path(path).attr({
                    stroke: bg.split("|")[0],
                    fill: "none", "stroke-width": bg.split("|")[1] || 3
                }),
            line: this.path(path).attr({
                stroke: color, fill: "none"
            }),
            from: obj1,
            to: obj2
        };
    }
};


// ┌────────────────────────────────────────────────────────────────────┐ \\
// │ openmdao variable node                                             │ \\
// └────────────────────────────────────────────────────────────────────┘ \\

Raphael.fn.variableNode = function(paper, x, y, name, attr, input) {
    var typeStr = attr.type.split('.'),
        border = '#0b93d5',  // default border color: blue
        rectObj, nameObj, typeObj, setObj;

    if (typeStr.length > 1) {
        typeStr = attr.units + ' (' + typeStr[typeStr.length-1] + ')';
    }
    else {
        typeStr = attr.units + ' (' + typeStr + ')';
    }

    // gray border if it's an input and already connected
    if (input && attr.connected) {
        border = '#666666';
    }

    rectObj = paper.rect(x, y, 150, 30, 10, 10)
        .attr({'stroke':border, 'fill':'#999999', 'stroke-width': 2}),
    nameObj = paper.text(x+75, y+10, openmdao.Util.getName(name))
        .attr({'text-anchor':'middle', 'font-size':'12pt'}),
    typeObj = paper.text(x+75, y+20, typeStr)
        .attr({'text-anchor':'middle', 'font-size':'10pt'});
    setObj = paper.set(rectObj, nameObj, typeObj);

    setObj.data('input',input);
    setObj.data('name',name);
    setObj.data('connected',attr.connected);

    // add classes for test/inspection
    rectObj.node.className.baseVal += ' variable-figure';
    nameObj.node.className.baseVal += ' variable-name';
    typeObj.node.className.baseVal += ' variable-type';

    return setObj;
};
