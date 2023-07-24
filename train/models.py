def fit(epoch, model, data_loader, criterion, optimizer, phase='valid', print_loss=True):
    if phase == 'train':
        model.train()
    if phase == 'valid':
        model.eval()
    
    running_loss = 0.0
    for batch_idx, (data, target) in enumerate(data_loader):
        
        if phase == 'train':
            optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        running_loss += loss.item()
        
        if phase == 'train':
            loss.backward()
            optimizer.step()
        
    loss = running_loss / len(data_loader.dataset)
    if print_loss:
        print (f'epoch:{epoch+1}, {phase}loss is {loss}')
    return loss