const fs = require('fs');

const jsonPath = process.argv[2];
if (!jsonPath) {
    console.error('Usage: node json-to-markdown.js <json-file>');
    process.exit(1);
}

const api = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

let md = '# CanvasKit API Reference\n\n';

// 顶层函数
if (api.functions.length) {
    md += '## 顶层函数\n';
    api.functions.forEach(f => md += `- \`${f}\`\n`);
    md += '\n';
}

// 命名空间（如 CanvasKit）
Object.keys(api.namespaces).forEach(ns => {
    md += `## \`${ns}\` 命名空间\n`;
    const members = api.namespaces[ns];
    if (members.functions.length) {
        md += '### 方法\n';
        members.functions.forEach(m => md += `- \`${m}\`\n`);
    }
    if (members.properties.length) {
        md += '### 属性\n';
        members.properties.forEach(p => md += `- \`${p}\`\n`);
    }
    md += '\n';
});

// 枚举
if (api.enums.length) {
    md += '## 枚举\n';
    api.enums.forEach(e => {
        md += `### \`${e.name}\`\n`;
        e.members.forEach(m => {
            md += `- \`${m.name}\` = \`${m.value}\`\n`;
        });
        md += '\n';
    });
}

// 接口
if (api.interfaces.length) {
    md += '## 接口\n';
    api.interfaces.forEach(i => md += `- \`${i}\`\n`);
    md += '\n';
}

// 类型别名
if (api.typeAliases.length) {
    md += '## 类型别名\n';
    api.typeAliases.forEach(t => md += `- \`${t}\`\n`);
    md += '\n';
}

fs.writeFileSync('API.md', md);
console.log('Markdown generated at API.md');
