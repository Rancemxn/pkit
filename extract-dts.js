const fs = require('fs');
const path = require('path');
const ts = require('typescript');

// 1. 确定 canvaskit-wasm 包的根目录
let packageRoot;
try {
    // 通过解析包的主入口找到根目录
    const mainPath = require.resolve('canvaskit-wasm');
    packageRoot = path.dirname(mainPath);
    // 如果主入口在 bin/ 下，则根目录是上一级
    if (packageRoot.endsWith('bin')) {
        packageRoot = path.dirname(packageRoot);
    }
} catch (e) {
    console.error('Cannot resolve canvaskit-wasm package.');
    process.exit(1);
}

// 2. 可能的 .d.ts 文件位置（按优先级）
const candidates = [
    path.join(packageRoot, 'types', 'index.d.ts'),
    path.join(packageRoot, 'index.d.ts'),
    path.join(packageRoot, 'canvaskit.d.ts'),
    path.join(packageRoot, 'bin', 'canvaskit.d.ts')
];

let dtsPath = null;
for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
        dtsPath = candidate;
        break;
    }
}

if (!dtsPath) {
    console.error('Could not find canvaskit.d.ts. Searched:');
    candidates.forEach(c => console.error(' - ' + c));
    process.exit(1);
}

console.log('Found .d.ts at:', dtsPath);

// 3. 读取并解析
const sourceCode = fs.readFileSync(dtsPath, 'utf-8');
const sourceFile = ts.createSourceFile(
    'canvaskit.d.ts',
    sourceCode,
    ts.ScriptTarget.Latest,
    true
);

// 4. 提取 API（后续代码与之前相同）
const api = {
    functions: [],
    classes: [],
    constants: [],
    enums: {},
    interfaces: [],
    typeAliases: []
};

function visit(node) {
    // 函数声明
    if (ts.isFunctionDeclaration(node) && node.name) {
        api.functions.push(node.name.text);
    }
    // 变量声明（常量）
    else if (ts.isVariableStatement(node)) {
        node.declarationList.declarations.forEach(decl => {
            if (ts.isVariableDeclaration(decl) && decl.name && ts.isIdentifier(decl.name)) {
                const name = decl.name.text;
                let value = undefined;
                if (decl.initializer) {
                    if (ts.isNumericLiteral(decl.initializer)) {
                        value = Number(decl.initializer.text);
                    } else if (ts.isStringLiteral(decl.initializer)) {
                        value = decl.initializer.text;
                    }
                }
                api.constants.push({ name, value });
            }
        });
    }
    // 类声明
    else if (ts.isClassDeclaration(node) && node.name) {
        const className = node.name.text;
        const methods = [];
        node.members.forEach(member => {
            if (ts.isMethodDeclaration(member) && member.name) {
                methods.push(member.name.getText(sourceFile));
            }
        });
        api.classes.push({ name: className, methods });
    }
    // 枚举声明
    else if (ts.isEnumDeclaration(node) && node.name) {
        const enumName = node.name.text;
        const members = {};
        node.members.forEach(member => {
            if (member.name) {
                const memberName = member.name.getText(sourceFile);
                let value = undefined;
                if (member.initializer) {
                    if (ts.isNumericLiteral(member.initializer)) {
                        value = Number(member.initializer.text);
                    }
                }
                members[memberName] = value;
            }
        });
        api.enums[enumName] = members;
    }
    // 接口
    else if (ts.isInterfaceDeclaration(node) && node.name) {
        api.interfaces.push(node.name.text);
    }
    // 类型别名
    else if (ts.isTypeAliasDeclaration(node) && node.name) {
        api.typeAliases.push(node.name.text);
    }

    ts.forEachChild(node, visit);
}

visit(sourceFile);

// 排序
api.functions.sort();
api.classes.sort((a, b) => a.name.localeCompare(b.name));
api.classes.forEach(cls => cls.methods.sort());
api.constants.sort((a, b) => a.name.localeCompare(b.name));
api.enums = Object.fromEntries(Object.entries(api.enums).sort(([a], [b]) => a.localeCompare(b)));
api.interfaces.sort();
api.typeAliases.sort();

// 输出 JSON
const outputPath = path.join(__dirname, 'canvaskit-api.json');
fs.writeFileSync(outputPath, JSON.stringify(api, null, 2), 'utf-8');
console.log(`API extracted to ${outputPath}`);
