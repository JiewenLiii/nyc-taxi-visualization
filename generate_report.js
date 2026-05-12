const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak
} = require("docx");


// 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "analysis")
REPORT_DIR = os.path.join(BASE_DIR, "report")

//自动创建输出目录
os.makedirs(REPORT_DIR, exist_ok=True)

// Helper functions
function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, bold: true, size: 36, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, bold: true, size: 30, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
  });
}

function heading3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, bold: true, size: 26, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
  });
}

function bodyText(text) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text, size: 22, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
  });
}

function bodyTextBold(text) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text, size: 22, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
  });
}

function imageBlock(imgPath, width, height) {
  const fullPath = path.join(ANALYSIS_DIR, imgPath);
  if (!fs.existsSync(fullPath)) {
    return bodyText(`[图片未找到: ${imgPath}]`);
  }
  const imgData = fs.readFileSync(fullPath);
  const ext = path.extname(imgPath).slice(1);
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({
      type: ext,
      data: imgData,
      transformation: { width, height },
      altText: { title: imgPath, description: imgPath, name: imgPath }
    })]
  });
}

function captionText(text) {
  return new Paragraph({
    spacing: { after: 160 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, size: 20, italics: true, color: "666666", font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
  });
}

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function tableCell(text, opts = {}) {
  return new TableCell({
    borders,
    width: opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
    shading: opts.header ? { fill: "2B6CB0", type: ShadingType.CLEAR } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({
        text,
        size: 20,
        bold: opts.header || false,
        color: opts.header ? "FFFFFF" : "000000",
        font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" }
      })]
    })]
  });
}

// Build document
const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" },
          size: 22
        }
      }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0, keepNext: false, keepLines: false } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1, keepNext: false, keepLines: false } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1200, bottom: 1440, left: 1200 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "\u7ebd\u7ea6\u5e02\u51fa\u79df\u8f66\u6570\u636e\u53ef\u89c6\u5316\u5206\u6790\u62a5\u544a", size: 18, color: "999999", font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "\u7b2c ", size: 18, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "999999" }),
            new TextRun({ text: " \u9875", size: 18, color: "999999" })
          ]
        })]
      })
    },
    children: [
      // ==================== 封面 ====================
      new Paragraph({ spacing: { before: 3000 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({ text: "\u6570\u636e\u53ef\u89c6\u5316\u5927\u4f5c\u4e1a\u62a5\u544a", size: 52, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 600 },
        children: [new TextRun({ text: "\u7ebd\u7ea6\u5e02\u51fa\u79df\u8f66\u6570\u636e\u53ef\u89c6\u5316\u5206\u6790\u7cfb\u7edf", size: 36, color: "2B6CB0", font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "\u2014\u2014 \u57fa\u4e8e2018\u5e74Yellow\u4e0eGreen\u51fa\u79df\u8f66\u884c\u7a0b\u6570\u636e", size: 26, color: "666666", font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
      }),
      new Paragraph({ spacing: { before: 800 } }),

      // 成员信息表
      new Table({
        width: { size: 8000, type: WidthType.DXA },
        columnWidths: [2000, 2000, 2000, 2000],
        rows: [
          new TableRow({ cantSplit: true, children: [
            tableCell("\u59d3\u540d", { header: true, width: 2000 }),
            tableCell("\u5b66\u53f7", { header: true, width: 2000 }),
            tableCell("\u9879\u76ee\u5b9a\u4f4d", { header: true, width: 2000 }),
            tableCell("\u4e3b\u8981\u5de5\u4f5c\u91cf", { header: true, width: 2000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u5f20\u4e09", { width: 2000 }),
            tableCell("202XXXXX01", { width: 2000 }),
            tableCell("\u9879\u76ee\u8d1f\u8d23\u4eba/\u6570\u636e\u5206\u6790", { width: 2000 }),
            tableCell("\u6570\u636e\u6e05\u6d17\u3001\u805a\u7c7b\u5206\u6790\u3001\u62a5\u544a\u64b0\u5199", { width: 2000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u674e\u56db", { width: 2000 }),
            tableCell("202XXXXX02", { width: 2000 }),
            tableCell("\u53ef\u89c6\u5316\u5f00\u53d1", { width: 2000 }),
            tableCell("ECharts\u5927\u5c4f\u5f00\u53d1\u3001\u4ea4\u4e92\u529f\u80fd", { width: 2000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u738b\u4e94", { width: 2000 }),
            tableCell("202XXXXX03", { width: 2000 }),
            tableCell("\u56fe\u8868\u5206\u6790", { width: 2000 }),
            tableCell("\u7edf\u8ba1\u56fe\u8868\u751f\u6210\u3001\u76f8\u5173\u6027\u5206\u6790", { width: 2000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u8d75\u516d", { width: 2000 }),
            tableCell("202XXXXX04", { width: 2000 }),
            tableCell("\u6570\u636e\u91c7\u96c6/\u5916\u90e8\u8054\u52a8", { width: 2000 }),
            tableCell("\u5929\u6c14\u6570\u636e\u83b7\u53d6\u3001\u8054\u52a8\u5206\u6790", { width: 2000 })
          ]})
        ]
      }),

      new Paragraph({ spacing: { before: 600 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "2026\u5e745\u6708", size: 24, color: "666666", font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" } })]
      }),

      // ==================== 目录页 ====================
      new Paragraph({ children: [new PageBreak()] }),
      heading1("\u76ee\u5f55"),
      bodyText("\u4e00\u3001\u9879\u76ee\u6982\u8ff0"),
      bodyText("\u4e8c\u3001\u9700\u6c42\u5206\u6790"),
      bodyText("\u4e09\u3001\u53ef\u884c\u6027\u5206\u6790"),
      bodyText("\u56db\u3001\u5de5\u5177\u4e0e\u6280\u672f\u6808"),
      bodyText("\u4e94\u3001\u6570\u636e\u6536\u96c6\u4e0e\u9884\u5904\u7406"),
      bodyText("\u516d\u3001\u6570\u636e\u7f3a\u5931\u503c\u68c0\u6d4b\u4e0e\u5904\u7406"),
      bodyText("\u4e03\u3001\u7edf\u8ba1\u5206\u6790\u4e0e\u53ef\u89c6\u5316"),
      bodyText("\u516b\u3001\u805a\u7c7b\u5206\u6790\u4e0e\u76f8\u4f3c\u6027"),
      bodyText("\u4e5d\u3001\u6570\u636e\u9884\u6d4b\u4e0e\u9a8c\u8bc1"),
      bodyText("\u5341\u3001\u5929\u6c14\u6570\u636e\u8054\u52a8\u5206\u6790"),
      bodyText("\u5341\u4e00\u3001\u5927\u5c4f\u53ef\u89c6\u5316\u7cfb\u7edf"),
      bodyText("\u5341\u4e8c\u3001\u4eba\u673a\u4ea4\u4e92\u4e0e\u52a8\u6001\u5c55\u793a"),
      bodyText("\u5341\u4e09\u3001\u6d4b\u8bd5\u7ed3\u679c\u4e0e\u5b8c\u6210\u60c5\u51b5"),
      bodyText("\u5341\u56db\u3001\u603b\u7ed3\u4e0e\u5c55\u671b"),

      // ==================== 第一章 ====================
      new Paragraph({ children: [new PageBreak()] }),
      heading1("\u4e00\u3001\u9879\u76ee\u6982\u8ff0"),
      bodyText("\u672c\u9879\u76ee\u57fa\u4e8e\u7ebd\u7ea6\u5e02\u51fa\u79df\u8f66\u4e0e\u8c6a\u534e\u8f7f\u8f66\u59d4\u5458\u4f1a(TLC)\u63d0\u4f9b\u76842018\u5e74\u5168\u5e74\u51fa\u79df\u8f66\u884c\u7a0b\u6570\u636e\uff0c\u5bf9\u7ebd\u7ea6\u5e02Yellow\uff08\u9ec4\u8272\uff09\u548cGreen\uff08\u7eff\u8272\uff09\u4e24\u5bb6\u51fa\u79df\u8f66\u516c\u53f8\u7684\u8fd0\u8425\u6570\u636e\u8fdb\u884c\u5168\u9762\u7684\u6570\u636e\u53ef\u89c6\u5316\u5206\u6790\u3002\u6570\u636e\u6db5\u76d6\u4e86\u884c\u7a0b\u65f6\u95f4\u3001\u4e0a\u4e0b\u8f66\u5730\u70b9\u3001\u884c\u7a0b\u8ddd\u79bb\u3001\u7968\u4ef7\u3001\u652f\u4ed8\u65b9\u5f0f\u3001\u4e58\u5ba2\u4eba\u6570\u7b49\u591a\u7ef4\u5ea6\u4fe1\u606f\u3002"),
      bodyText("\u9879\u76ee\u6570\u636e\u89c4\u6a21\uff1aYellow\u51fa\u79df\u8f66\u5168\u5e74\u7ea61.12\u4ebf\u6761\u884c\u7a0b\u8bb0\u5f55\uff0cGreen\u51fa\u79df\u8f66\u5168\u5e74\u7ea6855\u4e07\u6761\u884c\u7a0b\u8bb0\u5f55\uff0c\u5408\u8ba1\u8d85\u8fc71.2\u4ebf\u6761\u6570\u636e\u3002\u6570\u636e\u5b58\u50a8\u683c\u5f0f\u4e3aParquet\u5217\u5f0f\u5b58\u50a8\uff0c\u5171\u670919\u4e2a\u5b57\u6bb5\uff08Yellow\uff09\u548c20\u4e2a\u5b57\u6bb5\uff08Green\uff09\u3002"),
      bodyText("\u9879\u76ee\u76ee\u6807\uff1a\u901a\u8fc7\u6570\u636e\u6e05\u6d17\u3001\u7edf\u8ba1\u5206\u6790\u3001\u805a\u7c7b\u5efa\u6a21\u3001\u9884\u6d4b\u63a8\u5bfc\u3001\u5916\u90e8\u6570\u636e\u8054\u52a8\u7b49\u624b\u6bb5\uff0c\u6784\u5efa\u4e00\u4e2a\u529f\u80fd\u5b8c\u5584\u7684\u51fa\u79df\u8f66\u6570\u636e\u53ef\u89c6\u5316\u5206\u6790\u7cfb\u7edf\uff0c\u5e76\u4ee5\u5927\u5c4f\u6a21\u5f0f\u5c55\u793a\uff0c\u652f\u6301\u52a8\u6001\u65f6\u95f4\u53d8\u5316\u548c\u4eba\u673a\u4ea4\u4e92\u3002"),

      // ==================== 第二章 ====================
      heading1("\u4e8c\u3001\u9700\u6c42\u5206\u6790"),
      heading2("2.1 \u76ee\u6807\u7528\u6237"),
      bodyText("\u672c\u9879\u76ee\u7684\u76ee\u6807\u7528\u6237\u4e3b\u8981\u5305\u62ec\uff1a"),
      bodyText("\u2022 \u7ebd\u7ea6\u5e02\u51fa\u79df\u8f66\u4e0e\u8c6a\u534e\u8f7f\u8f66\u59d4\u5458\u4f1a(TLC)\uff1a\u4e86\u89e3\u51fa\u79df\u8f66\u884c\u4e1a\u8fd0\u8425\u72b6\u51b5\uff0c\u4f18\u5316\u76d1\u7ba1\u7b56\u7565"),
      bodyText("\u2022 \u51fa\u79df\u8f66\u516c\u53f8\u7ba1\u7406\u5c42\uff1a\u5206\u6790\u8fd0\u8425\u6548\u7387\u3001\u6536\u5165\u6a21\u5f0f\u3001\u53f8\u673a\u884c\u4e3a\u504f\u597d"),
      bodyText("\u2022 \u57ce\u5e02\u4ea4\u901a\u89c4\u5212\u90e8\u95e8\uff1a\u5206\u6790\u51fa\u884c\u9700\u6c42\u6ce2\u52a8\u89c4\u5f8b\uff0c\u8f85\u52a9\u4ea4\u901a\u7b56\u7565\u5236\u5b9a"),
      bodyText("\u2022 \u6570\u636e\u5206\u6790\u7814\u7a76\u4eba\u5458\uff1a\u63a2\u7d22\u5927\u89c4\u6a21\u4ea4\u901a\u6570\u636e\u7684\u5206\u6790\u65b9\u6cd5\u548c\u53ef\u89c6\u5316\u6280\u672f"),

      heading2("2.2 \u529f\u80fd\u9700\u6c42"),
      bodyText("\u6839\u636e\u4f5c\u4e1a\u8981\u6c42\uff0c\u672c\u9879\u76ee\u9700\u8981\u5b9e\u73b0\u4ee5\u4e0b\u529f\u80fd\uff1a"),
      bodyText("1. \u6570\u636e\u7f3a\u5931\u503c\u68c0\u6d4b\u4e0e\u5904\u7406"),
      bodyText("2. \u76f8\u4f9d\u6027\u3001\u76f8\u4f3c\u6027\u548c\u805a\u7c7b\u5206\u6790"),
      bodyText("3. \u591a\u79cd\u7edf\u8ba1\u56fe\u548c\u5206\u6790\u56fe"),
      bodyText("4. \u6570\u636e\u9884\u6d4b\u63a8\u5bfc\u4e0e\u9a8c\u8bc1"),
      bodyText("5. \u504f\u597d\u5206\u6790\u4e0e\u76f8\u5173\u6027\u5206\u6790"),
      bodyText("6. \u5927\u5c4f\u53ef\u89c6\u5316\u6574\u5408\uff08\u542b\u5730\u56fe\uff09"),
      bodyText("7. \u52a8\u6001\u65f6\u95f4\u53d8\u5316\u5c55\u793a"),
      bodyText("8. \u4eba\u673a\u4ea4\u4e92\u529f\u80fd"),
      bodyText("9. \u5916\u90e8\u6570\u636e\u8054\u52a8\uff08\u5929\u6c14\u6570\u636e\uff09"),

      // ==================== 第三章 ====================
      heading1("\u4e09\u3001\u53ef\u884c\u6027\u5206\u6790"),
      heading2("3.1 \u6280\u672f\u53ef\u884c\u6027"),
      bodyText("\u2022 Python 3.x + pandas\uff1a\u6210\u719f\u7684\u5927\u6570\u636e\u5904\u7406\u751f\u6001\uff0c\u652f\u6301Parquet\u683c\u5f0f\u8bfb\u53d6"),
      bodyText("\u2022 Apache ECharts 5\uff1a\u529f\u80fd\u5f3a\u5927\u7684\u53ef\u89c6\u5316\u5e93\uff0c\u652f\u6301\u4ea4\u4e92\u5f0f\u56fe\u8868\u548c\u5927\u5c4f\u5c55\u793a"),
      bodyText("\u2022 scikit-learn\uff1a\u63d0\u4f9bK-Means\u805a\u7c7b\u3001\u7ebf\u6027\u56de\u5f52\u3001PCA\u964d\u7ef4\u7b49\u7b97\u6cd5"),
      bodyText("\u2022 matplotlib/seaborn\uff1a\u751f\u6210\u9ad8\u8d28\u91cf\u7684\u9759\u6001\u5206\u6790\u56fe\u8868"),

      heading2("3.2 \u5de5\u4f5c\u91cf\u4f30\u7b97\uff08\u7518\u7279\u56fe\uff09"),
      // 甘特图用表格模拟
      new Table({
        width: { size: 9000, type: WidthType.DXA },
        columnWidths: [2500, 1500, 5000],
        rows: [
          new TableRow({ cantSplit: true, children: [
            tableCell("\u4efb\u52a1", { header: true, width: 2500 }),
            tableCell("\u5468\u671f", { header: true, width: 1500 }),
            tableCell("\u8fdb\u5ea6\u6761", { header: true, width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u6570\u636e\u6536\u96c6\u4e0e\u9884\u5904\u7406", { width: 2500 }),
            tableCell("\u7b2c1\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u7f3a\u5931\u503c\u5904\u7406\u4e0e\u6570\u636e\u6e05\u6d17", { width: 2500 }),
            tableCell("\u7b2c1-2\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u7edf\u8ba1\u56fe\u8868\u751f\u6210", { width: 2500 }),
            tableCell("\u7b2c2-3\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u805a\u7c7b\u4e0e\u76f8\u5173\u6027\u5206\u6790", { width: 2500 }),
            tableCell("\u7b2c3-4\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u9884\u6d4b\u6a21\u578b\u4e0e\u9a8c\u8bc1", { width: 2500 }),
            tableCell("\u7b2c4-5\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u5929\u6c14\u6570\u636e\u8054\u52a8", { width: 2500 }),
            tableCell("\u7b2c5-6\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("ECharts\u5927\u5c4f\u5f00\u53d1", { width: 2500 }),
            tableCell("\u7b2c6-8\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u4ea4\u4e92\u529f\u80fd\u4e0e\u52a8\u6001\u5c55\u793a", { width: 2500 }),
            tableCell("\u7b2c8-10\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u62a5\u544a\u64b0\u5199\u4e0e\u6f14\u793a\u51c6\u5907", { width: 2500 }),
            tableCell("\u7b2c10-12\u5468", { width: 1500 }),
            tableCell("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", { width: 5000 })
          ]})
        ]
      }),

      // ==================== 第四章 ====================
      heading1("\u56db\u3001\u5de5\u5177\u4e0e\u6280\u672f\u6808"),
      new Table({
        width: { size: 9000, type: WidthType.DXA },
        columnWidths: [2000, 3000, 4000],
        rows: [
          new TableRow({ cantSplit: true, children: [
            tableCell("\u7c7b\u522b", { header: true, width: 2000 }),
            tableCell("\u5de5\u5177", { header: true, width: 3000 }),
            tableCell("\u7528\u9014", { header: true, width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u6570\u636e\u5b58\u50a8", { width: 2000 }),
            tableCell("Parquet\u683c\u5f0f", { width: 3000 }),
            tableCell("\u5217\u5f0f\u5b58\u50a8\uff0c\u9ad8\u6548\u538b\u7f29\uff0c\u9002\u5408\u5927\u89c4\u6a21\u6570\u636e", { width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u6570\u636e\u5904\u7406", { width: 2000 }),
            tableCell("pandas, numpy", { width: 3000 }),
            tableCell("\u6570\u636e\u52a0\u8f7d\u3001\u6e05\u6d17\u3001\u805a\u5408\u3001\u7279\u5f81\u5de5\u7a0b", { width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u673a\u5668\u5b66\u4e60", { width: 2000 }),
            tableCell("scikit-learn", { width: 3000 }),
            tableCell("K-Means\u805a\u7c7b\u3001\u7ebf\u6027\u56de\u5f52\u3001PCA\u964d\u7ef4", { width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u9759\u6001\u53ef\u89c6\u5316", { width: 2000 }),
            tableCell("matplotlib, seaborn", { width: 3000 }),
            tableCell("\u7edf\u8ba1\u56fe\u8868\u3001\u70ed\u529b\u56fe\u3001\u805a\u7c7b\u53ef\u89c6\u5316", { width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u4ea4\u4e92\u53ef\u89c6\u5316", { width: 2000 }),
            tableCell("Apache ECharts 5", { width: 3000 }),
            tableCell("\u5927\u5c4f\u4eea\u8868\u76d8\u3001\u52a8\u6001\u56fe\u8868\u3001\u4ea4\u4e92\u7ec4\u4ef6", { width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u5916\u90e8\u6570\u636e", { width: 2000 }),
            tableCell("NOAA GHCND", { width: 3000 }),
            tableCell("\u7ebd\u7ea6\u4e2d\u592e\u516c\u56ed\u6c14\u8c61\u7ad9\u6570\u636e", { width: 4000 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u5f00\u53d1\u73af\u5883", { width: 2000 }),
            tableCell("Python 3.x, VS Code", { width: 3000 }),
            tableCell("\u4ee3\u7801\u5f00\u53d1\u4e0e\u8c03\u8bd5", { width: 4000 })
          ]})
        ]
      }),

      // ==================== 第五章 ====================
      heading1("\u4e94\u3001\u6570\u636e\u6536\u96c6\u4e0e\u9884\u5904\u7406"),
      heading2("5.1 \u6570\u636e\u6765\u6e90"),
      bodyText("\u6570\u636e\u6765\u6e90\u4e8e\u7ebd\u7ea6\u5e02\u51fa\u79df\u8f66\u548c\u8c6a\u534e\u8f7f\u8f66\u59d4\u5458\u4f1a(TLC)\u6388\u6743\u7684\u6280\u672f\u63d0\u4f9b\u5546\u6536\u96c6\u7684\u884c\u7a0b\u8bb0\u5f55\u3002\u539f\u59cb\u6570\u636e\u96c6\u5927\u5c0f\u7ea6400GB\uff0c\u672c\u9879\u76ee\u4f7f\u7528\u7684\u662f2018\u5e74\u5168\u5e74\u7684\u5b50\u96c6\uff0c\u91c7\u7528Parquet\u5217\u5f0f\u5b58\u50a8\u683c\u5f0f\uff0c\u5171\u670924\u4e2a\u6587\u4ef6\uff08Yellow\u548cGreen\u540412\u4e2a\u6708\uff09\u3002"),

      heading2("5.2 \u6570\u636e\u5b57\u6bb5"),
      bodyText("\u4e24\u5bb6\u516c\u53f8\u7684\u6570\u636e\u5b57\u6bb5\u57fa\u672c\u4e00\u81f4\uff0c\u4e3b\u8981\u5305\u62ec\uff1a"),
      bodyText("\u2022 VendorID\uff1a\u670d\u52a1\u5546\u4ee3\u7801\uff081=Creative Mobile, 2=VeriFone\uff09"),
      bodyText("\u2022 \u4e0a/\u4e0b\u8f66\u65f6\u95f4\uff1a\u8ba1\u4ef7\u5668\u542f\u52a8/\u5173\u95ed\u7684\u65e5\u671f\u548c\u65f6\u95f4"),
      bodyText("\u2022 \u4e58\u5ba2\u6570\u91cf\uff1a\u53f8\u673a\u624b\u52a8\u8f93\u5165\u7684\u503c"),
      bodyText("\u2022 \u884c\u7a0b\u8ddd\u79bb\uff1a\u8ba1\u4ef7\u5668\u62a5\u544a\u7684\u82f1\u91cc\u6570"),
      bodyText("\u2022 \u4e0a/\u4e0b\u8f66\u533a\u57dfID\uff1aTLC\u51fa\u79df\u8f66\u533a\u57df\u7f16\u7801"),
      bodyText("\u2022 \u8d39\u7387\u4ee3\u7801\u3001\u652f\u4ed8\u65b9\u5f0f\u3001\u8f66\u8d39\u3001\u5c0f\u8d39\u3001\u8fc7\u8def\u8d39\u3001\u603b\u989d\u7b49"),

      heading2("5.3 \u6570\u636e\u6e05\u6d17\u7b56\u7565"),
      bodyText("\u5bf9\u539f\u59cb\u6570\u636e\u6267\u884c\u4ee5\u4e0b\u6e05\u6d17\u64cd\u4f5c\uff1a"),
      bodyText("1. \u65f6\u95f4\u8303\u56f4\u8fc7\u6ee4\uff1a\u4ec5\u4fdd\u75592018\u5e74\u5185\u7684\u6570\u636e"),
      bodyText("2. \u884c\u7a0b\u65f6\u957f\u8fc7\u6ee4\uff1a\u4fdd\u75591\u5206\u949f\u5230600\u5206\u949f\u4e4b\u95f4\u7684\u884c\u7a0b"),
      bodyText("3. \u884c\u7a0b\u8ddd\u79bb\u8fc7\u6ee4\uff1a\u4fdd\u75590-200\u82f1\u91cc\u7684\u884c\u7a0b"),
      bodyText("4. \u8d39\u7528\u8fc7\u6ee4\uff1a\u8f66\u8d39\u548c\u603b\u989d\u57280-1000\u7f8e\u5143\u4e4b\u95f4"),
      bodyText("5. \u4e58\u5ba2\u6570\u8fc7\u6ee4\uff1a\u4fdd\u75591-9\u4eba"),
      bodyText("\u6e05\u6d17\u540eYellow\u4fdd\u7559\u7ea61.004\u4ebf\u6761\uff0cGreen\u4fdd\u7559\u7ea6855\u4e07\u6761\u3002"),

      // ==================== 第六章 ====================
      heading1("\u516d\u3001\u6570\u636e\u7f3a\u5931\u503c\u68c0\u6d4b\u4e0e\u5904\u7406"),
      bodyText("\u901a\u8fc7\u5bf9\u5168\u5e7412\u4e2a\u6708\u7684\u6570\u636e\u8fdb\u884c\u7f3a\u5931\u503c\u68c0\u6d4b\uff0c\u53d1\u73b0\u4ee5\u4e0b\u7f3a\u5931\u60c5\u51b5\uff1a"),
      bodyText("\u2022 Yellow\u51fa\u79df\u8f66\uff1acongestion_surcharge\u548cairport_fee\u5b57\u6bb5\u51e0\u4e4e\u5168\u90e8\u7f3a\u5931\uff08\u8fd199.99%\uff09\uff0c\u56e0\u4e3a\u8fd9\u4e24\u9879\u8d39\u7528\u57282019\u5e74\u624d\u5f00\u59cb\u5f81\u6536"),
      bodyText("\u2022 Green\u51fa\u79df\u8f66\uff1aehail_fee\u548ccongestion_surcharge\u5b57\u6bb5\u5168\u90e8\u7f3a\u5931\uff0ctrip_type\u4ec5\u67093\u6761\u7f3a\u5931"),
      bodyText("\u2022 \u5176\u4f59\u6838\u5fc3\u5b57\u6bb5\uff08\u65f6\u95f4\u3001\u8ddd\u79bb\u3001\u8d39\u7528\u3001\u5730\u70b9\u7b49\uff09\u65e0\u7f3a\u5931"),
      bodyText("\u5904\u7406\u7b56\u7565\uff1a\u5bf9\u4e8e\u5168\u90e8\u7f3a\u5931\u7684\u5b57\u6bb5\u76f4\u63a5\u5220\u9664\uff0c\u4e0d\u5f71\u54cd\u5206\u6790\u7ed3\u679c\u3002"),
      imageBlock("01_missing_values.png", 580, 220),
      captionText("\u56fe1\uff1aYellow\u4e0eGreen\u51fa\u79df\u8f66\u5b57\u6bb5\u7f3a\u5931\u7387\u5206\u6790"),

      // ==================== 第七章 ====================
      heading1("\u4e03\u3001\u7edf\u8ba1\u5206\u6790\u4e0e\u53ef\u89c6\u5316"),
      heading2("7.1 \u6708\u5ea6\u8d8b\u52bf\u5206\u6790"),
      bodyText("\u4ece\u6708\u5ea6\u8d8b\u52bf\u6765\u770b\uff0cYellow\u51fa\u79df\u8f66\u7684\u884c\u7a0b\u91cf\u57283\u6708\u548c4\u6708\u8fbe\u5230\u5cf0\u503c\uff08\u8d85\u8fc7900\u4e07\u6b21/\u6708\uff09\uff0c7\u6708\u548c8\u6708\u964d\u81f3\u4f4e\u8c37\uff08\u7ea6760\u4e07\u6b21/\u6708\uff09\u3002Green\u51fa\u79df\u8f66\u5448\u73b0\u76f8\u4f3c\u8d8b\u52bf\u4f46\u6570\u91cf\u4ec5\u4e3aYellow\u7684\u7ea61/11\u3002\u5e73\u5747\u8f66\u8d39\u548c\u884c\u7a0b\u8ddd\u79bb\u5728\u5168\u5e74\u4fdd\u6301\u76f8\u5bf9\u7a33\u5b9a\u3002"),
      imageBlock("02_monthly_trend.png", 580, 440),
      captionText("\u56fe2\uff1aYellow vs Green \u51fa\u79df\u8f662018\u5e74\u6708\u5ea6\u8d8b\u52bf\u5bf9\u6bd4"),

      heading2("7.2 24\u5c0f\u65f6\u8fd0\u8425\u6a21\u5f0f"),
      bodyText("\u4e24\u5bb6\u516c\u53f8\u5747\u5448\u73b0\u660e\u663e\u7684\u53cc\u5cf0\u6a21\u5f0f\uff1a\u65e9\u9ad8\u5cf0\uff087-9\u70b9\uff09\u548c\u665a\u9ad8\u5cf0\uff0817-19\u70b9\uff09\u3002\u51cc\u6668\u65f6\u6bb5\uff082-5\u70b9\uff09\u884c\u7a0b\u91cf\u6700\u4f4e\u3002\u5e73\u5747\u8f66\u8d39\u5728\u665a\u95f4\u548c\u51cc\u6668\u8f83\u9ad8\uff0c\u53ef\u80fd\u4e0e\u591c\u95f4\u9644\u52a0\u8d39\u548c\u5c11\u6709\u7684\u9ad8\u901f\u516c\u8def\u9009\u62e9\u6709\u5173\u3002"),
      imageBlock("03_hourly_pattern.png", 580, 440),
      captionText("\u56fe3\uff1a24\u5c0f\u65f6\u8fd0\u8425\u6a21\u5f0f\u5bf9\u6bd4"),

      heading2("7.3 \u661f\u671f\u6a21\u5f0f\u4e0e\u652f\u4ed8\u65b9\u5f0f"),
      bodyText("\u5de5\u4f5c\u65e5\u7684\u884c\u7a0b\u91cf\u660e\u663e\u9ad8\u4e8e\u5468\u672b\uff0c\u5468\u4e94\u662f\u5168\u5468\u884c\u7a0b\u91cf\u6700\u9ad8\u7684\u4e00\u5929\u3002\u652f\u4ed8\u65b9\u5f0f\u4e0a\uff0c\u4fe1\u7528\u5361\u652f\u4ed8\u5360\u636e\u7edd\u5bf9\u4e3b\u5bfc\u5730\u4f4d\uff08Yellow\u7ea676%\uff0cGreen\u7ea669%\uff09\uff0c\u73b0\u91d1\u652f\u4ed8\u7ea6\u536024%\u548c31%\u3002"),
      imageBlock("04_dow_pattern.png", 580, 200),
      captionText("\u56fe4\uff1a\u661f\u671f\u8fd0\u8425\u6a21\u5f0f\u5bf9\u6bd4"),
      imageBlock("05_payment_type.png", 560, 200),
      captionText("\u56fe5\uff1a\u652f\u4ed8\u65b9\u5f0f\u5206\u5e03"),

      heading2("7.4 \u884c\u653f\u533a\u5206\u6790\u4e0e\u70ed\u95e8\u8def\u7ebf"),
      bodyText("Manhattan\u662f\u6700\u4e3b\u8981\u7684\u51fa\u884c\u533a\u57df\uff0c\u5360Yellow\u51fa\u79df\u8f66\u884c\u7a0b\u7684\u7ea658%\u3002\u70ed\u95e8\u8def\u7ebf\u4e3b\u8981\u96c6\u4e2d\u5728Manhattan\u5185\u90e8\u533a\u57df\u95f4\u7684\u5f80\u8fd4\uff0c\u4ee5\u53caManhattan\u4e0e\u673a\u573a\u4e4b\u95f4\u7684\u5f80\u8fd4\u3002"),
      imageBlock("06_borough_analysis.png", 580, 260),
      captionText("\u56fe6\uff1a\u5404\u884c\u653f\u533a\u884c\u7a0b\u91cf\u5206\u6790"),
      imageBlock("10_top_routes.png", 580, 260),
      captionText("\u56fe7\uff1aTOP10\u70ed\u95e8\u8def\u7ebf"),

      // ==================== 第八章 ====================
      heading1("\u516b\u3001\u805a\u7c7b\u5206\u6790\u4e0e\u76f8\u4f3c\u6027"),
      heading2("8.1 K-Means\u805a\u7c7b"),
      bodyText("\u4f7f\u7528K-Means\u7b97\u6cd5\u5c06\u6708\u5ea6\u6570\u636e\u805a\u4e3a3\u7c7b\uff1a"),
      bodyText("\u2022 \u805a\u7c7b1\uff08\u4f4e\u5cf0\u4f4e\u4ef7\uff09\uff1a\u5305\u542b\u591a\u4e2a\u6708\u4efd\uff0c\u7279\u5f81\u4e3a\u8f83\u4f4e\u7684\u884c\u7a0b\u91cf\u548c\u8f66\u8d39"),
      bodyText("\u2022 \u805a\u7c7b2\uff08\u9ad8\u5cf0\u9ad8\u4ef7\uff09\uff1a\u4e3b\u8981\u4e3a\u590f\u5b63\u6708\u4efd\uff0c\u8f66\u8d39\u548c\u65f6\u957f\u8f83\u9ad8"),
      bodyText("\u2022 \u805a\u7c7b3\uff08\u4e2d\u7b49\u6c34\u5e73\uff09\uff1a\u4e3b\u8981\u4e3aGreen\u51fa\u79df\u8f66\u6570\u636e"),
      imageBlock("08_clustering_analysis.png", 580, 260),
      captionText("\u56fe8\uff1aK-Means\u805a\u7c7b\u7ed3\u679c\uff08PCA\u964d\u7ef4 + \u96f7\u8fbe\u56fe\uff09"),

      heading2("8.2 \u76f8\u5173\u6027\u5206\u6790"),
      bodyText("\u901a\u8fc7\u76ae\u5c14\u900a\u76f8\u5173\u7cfb\u6570\u5206\u6790\u53d1\u73b0\uff1a\u8f66\u8d39\u4e0e\u603b\u989d\u9ad8\u5ea6\u6b63\u76f8\u5173(r=0.98)\uff0c\u8f66\u8d39\u4e0e\u8ddd\u79bb\u5f3a\u6b63\u76f8\u5173(r=0.92)\uff0c\u884c\u7a0b\u6570\u4e0e\u8f66\u8d39\u5448\u8d1f\u76f8\u5173\uff0c\u8bf4\u660e\u9700\u6c42\u9ad8\u5cf0\u65f6\u8f66\u8d39\u5e76\u672a\u663e\u8457\u4e0a\u6da8\u3002"),
      imageBlock("07_correlation_heatmap.png", 580, 260),
      captionText("\u56fe9\uff1a\u5b57\u6bb5\u76f8\u5173\u6027\u70ed\u529b\u56fe"),

      // ==================== 第九章 ====================
      heading1("\u4e5d\u3001\u6570\u636e\u9884\u6d4b\u4e0e\u9a8c\u8bc1"),
      bodyText("\u4f7f\u7528\u7ebf\u6027\u56de\u5f52\u6a21\u578b\uff0c\u4ee5\u524d10\u4e2a\u6708\u7684\u6570\u636e\u4f5c\u4e3a\u8bad\u7ec3\u96c6\uff0c\u9884\u6d4b\u540e2\u4e2a\u6708\uff0811\u6708\u300112\u6708\uff09\u7684\u884c\u7a0b\u6570\u91cf\u3001\u5e73\u5747\u8f66\u8d39\u3001\u5e73\u5747\u8ddd\u79bb\u548c\u5e73\u5747\u603b\u989d\u3002"),
      bodyText("\u7ed3\u679c\u5206\u6790\uff1a"),
      bodyText("\u2022 \u884c\u7a0b\u6570\u91cf\u9884\u6d4b\u8bef\u5dee\u8f83\u5927\uff0c\u56e0\u4e3a\u7ebf\u6027\u6a21\u578b\u65e0\u6cd5\u6355\u6349\u5b63\u8282\u6027\u6ce2\u52a8"),
      bodyText("\u2022 \u5e73\u5747\u8f66\u8d39\u9884\u6d4b\u8f83\u4e3a\u51c6\u786e\uff0c\u56e0\u4e3a\u8f66\u8d39\u76f8\u5bf9\u7a33\u5b9a"),
      bodyText("\u2022 \u5efa\u8bae\u4f7f\u7528\u66f4\u590d\u6742\u7684\u65f6\u95f4\u5e8f\u5217\u6a21\u578b\uff08\u5982ARIMA\uff09\u63d0\u9ad8\u9884\u6d4b\u7cbe\u5ea6"),
      imageBlock("09_prediction_validation.png", 580, 440),
      captionText("\u56fe10\uff1a\u6570\u636e\u9884\u6d4b\u63a8\u5bfc\u4e0e\u9a8c\u8bc1\u5bf9\u6bd4"),

      // ==================== 第十章 ====================
      heading1("\u5341\u3001\u5929\u6c14\u6570\u636e\u8054\u52a8\u5206\u6790"),
      bodyText("\u4ece\u7f8e\u56fd\u56fd\u5bb6\u6c14\u5019\u6570\u636e\u4e2d\u5fc3(NCDC)\u83b7\u53d6\u7ebd\u7ea6\u4e2d\u592e\u516c\u56ed\u6c14\u8c61\u7ad9(GHCND:USW00094728)2018\u5e74\u7684\u6708\u5ea6\u6c14\u8c61\u6570\u636e\uff0c\u5305\u62ec\u6e29\u5ea6\u3001\u964d\u6c34\u3001\u964d\u96ea\u3001\u98ce\u901f\u3001\u6e7f\u5ea6\u7b49\u6307\u6807\uff0c\u5206\u6790\u5929\u6c14\u5bf9\u51fa\u79df\u8f66\u51fa\u884c\u7684\u5f71\u54cd\u3002"),
      bodyText("\u4e3b\u8981\u53d1\u73b0\uff1a"),
      bodyText("\u2022 \u6e29\u5ea6\u4e0e\u884c\u7a0b\u6570\u5448\u975e\u7ebf\u6027\u5173\u7cfb\uff1a\u6781\u7aef\u6e29\u5ea6\uff08\u51ac\u5b63\u4e25\u5bd2\u548c\u590f\u5b63\u9177\u6691\uff09\u90fd\u4f1a\u5bfc\u81f4\u884c\u7a0b\u6570\u4e0b\u964d"),
      bodyText("\u2022 \u964d\u96ea\u5bf9\u884c\u7a0b\u6570\u6709\u660e\u663e\u8d1f\u9762\u5f71\u54cd\uff0c\u6709\u964d\u96ea\u6708\u4efd\u7684\u884c\u7a0b\u6570\u660e\u663e\u4f4e\u4e8e\u65e0\u964d\u96ea\u6708\u4efd"),
      bodyText("\u2022 \u98ce\u901f\u4e0e\u884c\u7a0b\u65f6\u957f\u5448\u6b63\u76f8\u5173\uff0c\u5927\u98ce\u5929\u6c14\u53ef\u80fd\u5bfc\u81f4\u884c\u7a0b\u65f6\u95f4\u589e\u52a0"),
      imageBlock("13_weather_correlation.png", 580, 460),
      captionText("\u56fe11\uff1a\u5929\u6c14\u6570\u636e\u8054\u52a8\u5206\u6790\u7efc\u5408\u56fe"),

      // ==================== 第十一章 ====================
      heading1("\u5341\u4e00\u3001\u5927\u5c4f\u53ef\u89c6\u5316\u7cfb\u7edf"),
      bodyText("\u57fa\u4e8eApache ECharts 5\u6784\u5efa\u4e86\u4e00\u4e2a\u5168\u529f\u80fd\u7684\u6570\u636e\u53ef\u89c6\u5316\u5927\u5c4f\u7cfb\u7edf\uff0c\u91c7\u7528\u6df1\u8272\u4e3b\u9898\u8bbe\u8ba1\uff0cCSS Grid\u5e03\u5c40\u3002\u5927\u5c4f\u5305\u542b10\u4e2a\u56fe\u8868\u6a21\u5757\uff1a"),
      bodyText("1. \u6807\u9898\u680f + \u5b9e\u65f6\u65f6\u949f"),
      bodyText("2. 4\u4e2aKPI\u6307\u6807\u5361\u7247\uff08\u603b\u884c\u7a0b\u6570\u3001\u603b\u6536\u5165\u3001\u5e73\u5747\u8f66\u8d39\u3001\u5e73\u5747\u65f6\u957f\uff09"),
      bodyText("3. \u6708\u5ea6\u884c\u7a0b\u8d8b\u52bf\u6298\u7ebf\u56fe"),
      bodyText("4. 24\u5c0f\u65f6\u884c\u7a0b\u70ed\u529b\u56fe"),
      bodyText("5. \u884c\u653f\u533a\u884c\u7a0b\u91cf\u67f1\u72b6\u56fe"),
      bodyText("6. \u652f\u4ed8\u65b9\u5f0f\u73af\u5f62\u56fe"),
      bodyText("7. \u76f8\u5173\u6027\u70ed\u529b\u56fe"),
      bodyText("8. PCA\u805a\u7c7b\u6563\u70b9\u56fe"),
      bodyText("9. \u70ed\u95e8\u8def\u7ebfTOP10\u6761\u5f62\u56fe"),
      bodyText("10. \u9884\u6d4b\u9a8c\u8bc1\u5bf9\u6bd4\u56fe"),
      bodyText("\u5927\u5c4f\u6587\u4ef6\u4f4d\u4e8e dashboard/index.html\uff0c\u53ef\u76f4\u63a5\u5728\u6d4f\u89c8\u5668\u4e2d\u6253\u5f00\u3002"),

      // ==================== 第十二章 ====================
      heading1("\u5341\u4e8c\u3001\u4eba\u673a\u4ea4\u4e92\u4e0e\u52a8\u6001\u5c55\u793a"),
      heading2("12.1 \u4eba\u673a\u4ea4\u4e92\u529f\u80fd"),
      bodyText("\u2022 \u6708\u4efd\u4e0b\u62c9\u9009\u62e9\u5668\uff1a\u9009\u62e9\u67d0\u4e2a\u6708\u4efd\u540e\uff0c\u6240\u6709\u56fe\u8868\u8054\u52a8\u66f4\u65b0"),
      bodyText("\u2022 \u81ea\u52a8\u64ad\u653e\u6309\u94ae\uff1a\u70b9\u51fb\u540e\u6bcf2\u79d2\u81ea\u52a8\u5207\u6362\u6708\u4efd\uff0c\u518d\u6b21\u70b9\u51fb\u6682\u505c"),
      bodyText("\u2022 \u884c\u653f\u533a\u70b9\u51fb\u5f39\u7a97\uff1a\u70b9\u51fb\u67f1\u72b6\u56fe\u5f39\u51fa\u8be6\u7ec6\u4fe1\u606f\u6a21\u6001\u6846"),
      bodyText("\u2022 \u56fe\u8868\u60ac\u505c\u63d0\u793a\uff1a\u9f20\u6807\u60ac\u505c\u663e\u793a\u8be6\u7ec6\u6570\u636e\u4fe1\u606f"),

      heading2("12.2 \u52a8\u6001\u65f6\u95f4\u53d8\u5316"),
      bodyText("\u2022 KPI\u6570\u5b57\u6eda\u52a8\u52a8\u753b\uff1a\u6570\u5b57\u4ece0\u6eda\u52a8\u5230\u76ee\u6807\u503c"),
      bodyText("\u2022 \u6708\u4efd\u81ea\u52a8\u5207\u6362\u65f6\u56fe\u8868\u5e73\u6ed1\u8fc7\u6e21\u52a8\u753b"),
      bodyText("\u2022 \u5b9e\u65f6\u65f6\u949f\u66f4\u65b0"),

      // ==================== 第十三章 ====================
      heading1("\u5341\u4e09\u3001\u6d4b\u8bd5\u7ed3\u679c\u4e0e\u5b8c\u6210\u60c5\u51b5"),
      heading2("13.1 \u7efc\u5408\u504f\u597d\u5206\u6790"),
      imageBlock("11_preferences_analysis.png", 580, 460),
      captionText("\u56fe12\uff1a\u7ebd\u7ea6\u51fa\u79df\u8f66\u7efc\u5408\u504f\u597d\u5206\u6790"),
      imageBlock("12_boxplot_comparison.png", 580, 340),
      captionText("\u56fe13\uff1aYellow vs Green \u5404\u6307\u6807\u7bb1\u7ebf\u56fe\u5bf9\u6bd4"),

      heading2("13.2 \u9700\u6c42\u5b8c\u6210\u5bf9\u6bd4"),
      new Table({
        width: { size: 9000, type: WidthType.DXA },
        columnWidths: [4500, 2250, 2250],
        rows: [
          new TableRow({ cantSplit: true, children: [
            tableCell("\u9700\u6c42\u9879", { header: true, width: 4500 }),
            tableCell("\u5b8c\u6210\u72b6\u6001", { header: true, width: 2250 }),
            tableCell("\u5bf9\u5e94\u56fe\u8868/\u529f\u80fd", { header: true, width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u7f3a\u5931\u503c\u68c0\u6d4b\u4e0e\u5904\u7406", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u56fe1", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u76f8\u4f9d\u6027/\u76f8\u4f3c\u6027/\u805a\u7c7b", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u56fe8\u3001\u56fe9", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u591a\u79cd\u7edf\u8ba1\u56fe\u548c\u5206\u6790\u56fe", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u56fe2-7\u3001\u56fe12-13", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u6570\u636e\u9884\u6d4b\u63a8\u5bfc\u4e0e\u9a8c\u8bc1", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u56fe10", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u504f\u597d\u5206\u6790\u4e0e\u76f8\u5173\u6027", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u56fe9\u3001\u56fe12", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u5927\u5c4f\u53ef\u89c6\u5316\u6574\u5408", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("dashboard/index.html", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u52a8\u6001\u65f6\u95f4\u53d8\u5316", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u81ea\u52a8\u64ad\u653e+\u6570\u5b57\u52a8\u753b", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u4eba\u673a\u4ea4\u4e92", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u8054\u52a8\u7b5b\u9009+\u5f39\u7a97+\u63d0\u793a", { width: 2250 })
          ]}),
          new TableRow({ cantSplit: true, children: [
            tableCell("\u5916\u90e8\u6570\u636e\u8054\u52a8", { width: 4500 }),
            tableCell("\u2713 \u5df2\u5b8c\u6210", { width: 2250 }),
            tableCell("\u56fe11\uff08\u5929\u6c14\u6570\u636e\uff09", { width: 2250 })
          ]})
        ]
      }),

      // ==================== 第十四章 ====================
      heading1("\u5341\u56db\u3001\u603b\u7ed3\u4e0e\u5c55\u671b"),
      bodyText("\u672c\u9879\u76ee\u5b8c\u6210\u4e86\u5bf9\u7ebd\u7ea6\u5e02Yellow\u548cGreen\u4e24\u5bb6\u51fa\u79df\u8f66\u516c\u53f82018\u5e74\u5168\u5e74\u8d85\u8fc71.2\u4ebf\u6761\u884c\u7a0b\u6570\u636e\u7684\u5168\u9762\u53ef\u89c6\u5316\u5206\u6790\u3002\u4e3b\u8981\u6210\u679c\u5305\u62ec\uff1a"),
      bodyText("1. \u5b8c\u6210\u4e86\u6570\u636e\u6e05\u6d17\u3001\u7f3a\u5931\u503c\u5904\u7406\u548c\u7279\u5f81\u5de5\u7a0b"),
      bodyText("2. \u751f\u6210\u4e8613\u5f20\u9ad8\u8d28\u91cf\u5206\u6790\u56fe\u8868\uff0c\u6db5\u76d6\u8d8b\u52bf\u3001\u6a21\u5f0f\u3001\u805a\u7c7b\u3001\u76f8\u5173\u6027\u3001\u9884\u6d4b\u7b49\u591a\u4e2a\u7ef4\u5ea6"),
      bodyText("3. \u6784\u5efa\u4e86\u529f\u80fd\u5b8c\u5584\u7684ECharts\u5927\u5c4f\u53ef\u89c6\u5316\u7cfb\u7edf\uff0c\u652f\u6301\u52a8\u6001\u5c55\u793a\u548c\u4eba\u673a\u4ea4\u4e92"),
      bodyText("4. \u5b9e\u73b0\u4e86\u5929\u6c14\u6570\u636e\u8054\u52a8\u5206\u6790\uff0c\u63ed\u793a\u4e86\u5929\u6c14\u5bf9\u51fa\u79df\u8f66\u51fa\u884c\u7684\u5f71\u54cd"),
      bodyText("\u672a\u6765\u6539\u8fdb\u65b9\u5411\uff1a"),
      bodyText("\u2022 \u5f15\u5165\u66f4\u591a\u5916\u90e8\u6570\u636e\u6e90\uff08\u5982\u5730\u94c1\u6570\u636e\u3001\u6d3b\u52a8\u6570\u636e\u7b49\uff09"),
      bodyText("\u2022 \u91c7\u7528\u66f4\u590d\u6742\u7684\u65f6\u95f4\u5e8f\u5217\u6a21\u578b\uff08ARIMA\u3001LSTM\uff09\u63d0\u9ad8\u9884\u6d4b\u7cbe\u5ea6"),
      bodyText("\u2022 \u96c6\u6210\u5730\u56feAPI\u5b9e\u73b0\u771f\u5b9e\u7684\u5730\u7406\u7a7a\u95f4\u53ef\u89c6\u5316"),
      bodyText("\u2022 \u4f18\u5316\u5927\u5c4f\u54cd\u5e94\u901f\u5ea6\u548c\u89c6\u89c9\u6548\u679c"),
    ]
  }]
});

// Generate
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log("Report generated: " + OUTPUT_PATH);
}).catch(err => {
  console.error("Error:", err);
});
