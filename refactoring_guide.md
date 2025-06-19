# Code Refactoring Checklist & Guidelines
## AI Assistant Instructions for Code Review

## 🎯 Primary Refactoring Goals
**ALWAYS preserve existing functionality while improving:**
- Code clarity and readability
- Performance and efficiency  
- Maintainability and organization
- Elimination of repetitive code

## 📋 Mandatory Refactoring Checklist

### **Code Quality & Organization**
- [ ] **Remove ALL duplicate code** - Extract repeated logic into reusable functions
- [ ] **Simplify complex functions** - Break down functions doing multiple things
- [ ] **Improve naming** - Use clear, descriptive variable and function names
- [ ] **Add missing error handling** - Ensure robust error management
- [ ] **Organize imports** - Remove unused imports, group logically
- [ ] **Eliminate dead code** - Remove unused variables, functions, commented code
- [ ] **Consistent formatting** - Apply consistent indentation and spacing

### **Performance Optimization**
- [ ] **Identify slow operations** - Flag inefficient loops, database queries, network calls
- [ ] **Suggest caching opportunities** - Where repeated operations can be cached
- [ ] **Optimize data structures** - Use appropriate data types and structures
- [ ] **Reduce unnecessary operations** - Eliminate redundant processing
- [ ] **Improve algorithm efficiency** - Suggest better algorithmic approaches

### **Code Structure & Patterns**
- [ ] **Ensure single responsibility** - Each function should do one thing well
- [ ] **Improve separation of concerns** - Separate UI, logic, and data operations
- [ ] **Apply DRY principle** - Don't Repeat Yourself - extract common patterns
- [ ] **Enhance modularity** - Make code more reusable and maintainable
- [ ] **Standardize patterns** - Use consistent approaches across similar code

## 🤖 AI Assistant Commands & Rules

### **When User Requests Refactoring:**

1. **ALWAYS ask for context first:**
   - "What type of file(s) are you reviewing? (scraper, GUI, database, etc.)"
   - "How does this code interact with the rest of the project?"
   - "Are there any specific concerns or performance issues you've noticed?"

2. **BEFORE suggesting changes:**
   - Read and understand the code's purpose and dependencies
   - Identify the code's role in the larger system
   - Note any external integrations or requirements

3. **WHEN reviewing code:**
   - Go through the entire checklist systematically
   - Point out EVERY instance of duplicate code
   - Suggest specific improvements with explanations
   - Show before/after examples for complex changes

4. **ALWAYS provide:**
   - Clear explanation of WHY each change improves the code
   - Consideration of potential risks or side effects
   - Step-by-step implementation suggestions
   - Priority ranking (critical vs. nice-to-have improvements)

### **Refactoring Process Rules:**

**RULE 1: Safety First**
- Never break existing functionality
- Maintain all current interfaces and APIs
- Preserve existing behavior exactly

**RULE 2: One Thing at a Time**
- Focus on one type of improvement per review
- Don't mix performance optimizations with structural changes
- Make incremental, testable improvements

**RULE 3: Context Awareness**
- Consider how changes affect other parts of the system
- Respect existing architectural patterns
- Maintain consistency with project conventions

**RULE 4: Clear Communication**
- Explain the reasoning behind each suggestion
- Provide concrete examples of improvements
- Estimate the impact/benefit of each change

**RULE 5: Prioritize Impact**
- Focus on changes that provide the most benefit
- Address critical issues (performance, bugs) first
- Consider maintenance burden vs. benefit

## 📝 Required Review Format

When reviewing code, structure your response as:

### **1. Code Analysis**
- Purpose and current functionality
- Dependencies and interactions
- Identified issues and improvements

### **2. Critical Issues** (if any)
- Performance bottlenecks
- Potential bugs or error conditions
- Security or reliability concerns

### **3. Duplicate Code Elimination**
- List ALL instances of repeated code
- Suggest extraction patterns and shared functions
- Show how to consolidate similar logic

### **4. Structural Improvements**
- Function organization and responsibility
- Naming and clarity improvements
- Error handling enhancements

### **5. Performance Optimizations**
- Specific slow operations identified
- Suggested optimizations with expected impact
- Caching or efficiency opportunities

### **6. Implementation Priority**
- **High Priority:** Critical fixes and major duplications
- **Medium Priority:** Performance improvements and organization
- **Low Priority:** Minor clarity and style improvements

## ⚠️ What NOT to Change

**DO NOT suggest changes that:**
- Break existing APIs or interfaces
- Require major architectural rewrites
- Add unnecessary complexity
- Change external behavior
- Introduce new dependencies without clear benefit

**ALWAYS preserve:**
- Current functionality and behavior
- Existing error handling patterns (unless improving them)
- Integration points with other system components
- User-facing interfaces and workflows

## 🎯 Focus Areas by Code Type

**When user specifies code type, emphasize:**

**Scraper Files:** Performance, error handling, duplicate request logic
**GUI Files:** UI responsiveness, event handling, consistent styling patterns  
**Database Files:** Query efficiency, connection management, data validation
**Core Logic:** Algorithm efficiency, error propagation, modular design
**Configuration:** Flexibility, validation, default handling
**Background Tasks:** Resource management, error recovery, scheduling efficiency

Remember: The goal is clean, efficient, maintainable code that works exactly like the original but better.